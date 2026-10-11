"""Build the approved local dataset and TMDL fallback; no engine success claim."""
import json
from pathlib import Path
import pandas as pd
from previewlib import ROOT, load, generate, validate, reconcile, scenario_checks, write_json, DISCLOSURE
from prepare_model import prepare

DATA = ROOT / 'data/vibe_dashboarding_test'
DOCS = ROOT / 'docs/vibe_dashboarding_test'
PROJECT = ROOT / 'powerbi/vibe_dashboarding_test'

def cohort_activity(users, events, cutoff):
    users = users.copy()
    users['SignupCohort'] = pd.to_datetime(users.SignupDate).dt.to_period('M')
    joined = events.merge(users, on='UserId')
    joined['ActivityMonth'] = pd.to_datetime(joined.Date).dt.to_period('M')
    active = set(zip(joined.UserId, joined.ActivityMonth))
    end = pd.Period(cutoff, freq='M')
    rows = []
    for user in users.itertuples():
        for age in range(end.ordinal - user.SignupCohort.ordinal + 1):
            month = user.SignupCohort + age
            rows.append({'UserId': user.UserId, 'Age': age, 'Active': int((user.UserId, month) in active)})
    return pd.DataFrame(rows)

def ident(value):
    return "'" + value.replace("'", "''") + "'"

def main():
    cfg = load(ROOT/'config/dashboard.yaml')
    cfg.update(name='vibe_dashboarding_test', required_pages=['Performance', 'Engagement', 'Cohort Retention'])
    cfg['generation'].update(start='2026-01-01', end='2026-06-30', users=1200, events=18000, granularity='monthly')
    write_json(ROOT/'config/vibe_dashboarding_test.yaml', cfg)
    schema, metrics = load(ROOT/'config/schema.yaml'), load(ROOT/'config/metrics.yaml')
    tables = generate(cfg['generation'])
    errors = validate(tables, schema)
    scenarios = scenario_checks(tables, cfg['generation'])
    assert not errors, errors
    assert all(s['status'] == 'PASS' for s in scenarios), scenarios
    totals, monthly = reconcile(tables, 'monthly')
    assert totals['additive_reconciliation']
    DATA.mkdir(parents=True, exist_ok=True)
    for name, frame in tables.items():
        frame.to_csv(DATA/f'{name}.csv', index=False)
    activity = cohort_activity(tables['Users'], tables['Events'], cfg['generation']['end'])
    assert not activity.duplicated(['UserId', 'Age']).any()
    activity.to_csv(DATA/'CohortActivity.csv', index=False)
    pd.DataFrame({'Age': range(6)}).to_csv(DATA/'CohortAge.csv', index=False)
    monthly.to_csv(DATA/'reconciliation_by_period.csv')
    write_json(DATA/'manifest.json', {'disclosure':DISCLOSURE,'generation':cfg['generation'],'rows':{**{k:len(v) for k,v in tables.items()},'CohortActivity':len(activity),'CohortAge':6}})
    write_json(DOCS/'data_validation.json', {'status':'PASS','errors':errors,'scenario_checks':scenarios,'totals':totals})
    write_json(DOCS/'reconciliation.json', totals)
    cohort = activity.merge(tables['Users'], on='UserId')
    cohort['SignupCohort'] = pd.to_datetime(cohort.SignupDate).dt.strftime('%Y-%m-01')
    oracle = cohort.groupby(['SignupCohort','Age','Segment']).agg(EligibleUsers=('UserId','nunique'),RetainedUsers=('Active','sum')).reset_index()
    oracle['RetentionRate'] = oracle.RetainedUsers / oracle.EligibleUsers
    assert oracle.RetentionRate.between(0,1).all()
    oracle.to_csv(DOCS/'cohort_reconciliation.csv', index=False)
    inputs = prepare(schema, metrics, DATA)
    inputs['tables'][0]['columns']['SignupCohort'] = 'date'
    inputs['tables'][0]['m'] = inputs['tables'][0]['m'].replace('in\n    Typed', '    , Cohort = Table.AddColumn(Typed, "SignupCohort", each Date.StartOfMonth([SignupDate]), type date)\nin\n    Cohort')
    date = next(t for t in inputs['tables'] if t['name']=='Date')
    date['columns']['MonthStart'] = 'date'
    date['m'] = date['m'].replace('in\n    Typed', '    , Months = Table.AddColumn(Typed, "MonthStart", each Date.StartOfMonth([Date]), type date)\nin\n    Months')
    helper_schema = {'tables':{'CohortActivity':{'primary_key':'UserId','columns':{'UserId':'int64','Age':'int64','Active':'int64'}},'CohortAge':{'primary_key':'Age','columns':{'Age':'int64'}}},'relationships':[]}
    helpers = prepare(helper_schema, {'measures':[]}, DATA)['tables']
    helpers[0]['hidden_columns'] = ['UserId','Age','Active']
    helpers[1]['hidden_columns'] = []
    inputs['tables'] += helpers
    inputs['relationships'] += [dict(from_table='CohortActivity',from_column='UserId',to_table='Users',to_column='UserId'),dict(from_table='CohortActivity',from_column='Age',to_table='CohortAge',to_column='Age')]
    extensions = [
        dict(name='Sessions',table='Events',dax='COUNTROWS(Events)',format='#,##0',folder='Activity',contract='Eligible event sessions in current filter.'),
        dict(name='Cohort Size',table='Users',dax='COUNTROWS(Users)',format='#,##0',folder='Retention',contract='All enrolled users in selected cohort and segment.'),
        dict(name='Eligible Cohort Users',table='CohortActivity',dax="CALCULATE(DISTINCTCOUNT(CohortActivity[UserId]), REMOVEFILTERS('Date'))",format='#,##0',folder='Retention',contract='Distinct enrolled users with an observed age cell; excludes future cohort-age combinations.'),
        dict(name='Retained Users',table='CohortActivity',dax="VAR Eligible = [Eligible Cohort Users] RETURN IF(ISBLANK(Eligible), BLANK(), COALESCE(CALCULATE(DISTINCTCOUNT(CohortActivity[UserId]), CohortActivity[Active] = 1, REMOVEFILTERS('Date')), 0))",format='#,##0',folder='Retention',contract='Distinct cohort users active in observed age months; zero if observed but inactive, blank if future.'),
        dict(name='Retention Rate',table='CohortActivity',dax='DIVIDE([Retained Users], [Eligible Cohort Users])',format='0.0%',folder='Retention',contract='Distinct retained population / distinct eligible cohort population; totals recompute both sets.')]
    inputs['measures'] += extensions
    write_json(ROOT/'config/vibe_metric_extensions.yaml', {'measures':extensions,'cohort_contract':'Signup-month cohort; distinct activity in calendar month of age; future cells blank; segment filters both sets; fixed 2026-06-30 cutoff.'})
    write_json(DOCS/'model_authoring_inputs.json', inputs)
    model = PROJECT/'vibe_dashboarding_test.SemanticModel'
    definition = model/'definition'
    (definition/'tables').mkdir(parents=True, exist_ok=True)
    write_json(model/'definition.pbism', {'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json','version':'4.2','settings':{'qnaEnabled':False}})
    (definition/'database.tmdl').write_text('database vibe_dashboarding_test\n\tcompatibilityLevel: 1604\n', encoding='utf-8')
    (definition/'model.tmdl').write_text('model Model\n\tculture: en-US\n\tdefaultPowerBIDataSourceVersion: powerBI_V3\n\tsourceQueryCulture: en-US\n\tdiscourageImplicitMeasures\n\n'+''.join('ref table '+ident(t['name'])+'\n' for t in inputs['tables'])+'\nref expression pMockDataRoot\n',encoding='utf-8')
    (definition/'expressions.tmdl').write_text('expression pMockDataRoot = '+inputs['parameter']['m']+'\n\tkind: m\n',encoding='utf-8')
    rels=[]
    for i,r in enumerate(inputs['relationships']):
        rels.append(f"relationship vibe_relationship_{i}\n\tfromColumn: {ident(r['from_table'])}.{ident(r['from_column'])}\n\ttoColumn: {ident(r['to_table'])}.{ident(r['to_column'])}\n\tcrossFilteringBehavior: oneDirection\n")
    (definition/'relationships.tmdl').write_text('\n'.join(rels),encoding='utf-8')
    for t in inputs['tables']:
        lines=['/// '+DISCLOSURE+'; '+t['name']+' local Import table.', 'table '+ident(t['name'])]
        if t['name']=='Date': lines += ['\tdataCategory: Time']
        for m in inputs['measures']:
            if m['table'] != t['name']: continue
            lines += ['', '\t/// '+m['contract'], '\tmeasure '+ident(m['name'])+' = '+m['dax'], '\t\tformatString: '+m['format'], '\t\tdisplayFolder: '+m['folder']]
        for col,typ in t['columns'].items():
            lines += ['', '\tcolumn '+ident(col), '\t\tdataType: '+{'date':'dateTime','int64':'int64','string':'string','double':'double'}[typ], '\t\tsourceColumn: '+col, '\t\tsummarizeBy: none']
            if col in t['hidden_columns'] or (t['name']=='Events' and col in ['Converted','RevenueCents','SessionMinutes']): lines += ['\t\tisHidden']
            if typ=='date': lines += ['\t\tformatString: '+('MMM yyyy' if col in ['MonthStart','SignupCohort'] else 'yyyy-MM-dd')]
            if col=='MonthName': lines += ['\t\tsortByColumn: Month']
            if t['name']=='Date' and col=='Date': lines += ['\t\tisKey']
        lines += ['', '\tpartition '+ident(t['name'])+' = m', '\t\tmode: import', '\t\tsource =', *['\t\t\t'+s for s in t['m'].splitlines()]]
        (definition/'tables'/f"{t['name']}.tmdl").write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'data':'PASS','totals':totals,'cohort_cells':len(oracle),'model':'TMDL authored; engine/refresh NOT VERIFIED'}))

if __name__ == '__main__': main()
