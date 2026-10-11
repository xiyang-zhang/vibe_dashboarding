// Author from the approved brief into the official Microsoft CLI scaffold.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const root = path.resolve(__dirname, '..');
const report = path.join(root, 'powerbi/vibe_dashboarding_test/vibe_dashboarding_test.Report');
const read = p => JSON.parse(fs.readFileSync(p, 'utf8').replace(/^\uFEFF/, ''));
const write = (p,v) => { fs.mkdirSync(path.dirname(p),{recursive:true}); fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n'); };
const briefText = fs.readFileSync(path.join(root,'_brief/report-spec.md'),'utf8');
const brief = JSON.parse(briefText.split('```yaml')[1].split('```')[0])['Design Brief'];
const inputs = read(path.join(root,'docs/vibe_dashboarding_test/model_authoring_inputs.json'));
const measures = new Map(inputs.measures.map(m=>[m.name,m.table]));
const colors = Object.fromEntries(brief.color_map.map(m=>[m.measure,m.color]));
const id = s => crypto.createHash('sha256').update('vibe_dashboarding_test:'+s).digest('hex').slice(0,20);
const lit = v => ({expr:{Literal:{Value:typeof v==='string'?"'"+v.replace(/'/g,"''")+"'":typeof v==='boolean'?String(v):v+'D'}}});
const fill = v => ({solid:{color:lit(v)}});
const entry = (properties,selector) => [{properties,...(selector?{selector}: {})}];
const proj = binding => {
  const [,table,property] = binding.match(/^(.+)\[(.+)\]$/);
  const actual = measures.get(property) || table;
  return {field:{[measures.has(property)?'Measure':'Column']:{Expression:{SourceRef:{Entity:actual}},Property:property}},queryRef:actual+'.'+property,nativeQueryRef:property};
};
const spec = {
  $schema:'https://vega.github.io/schema/vega-lite/v5.json',data:{name:'dataset'},
  width:'container',height:'container',autosize:{type:'fit',contains:'padding'},
  background:'#161D44',padding:24,
  transform:[{filter:'isValid(datum["Retention Rate"])'},{calculate:'timeFormat(toDate(datum.SignupCohort), "%b %Y")',as:'Cohort'}],
  encoding:{x:{field:'Age',type:'ordinal',sort:[0,1,2,3,4,5],title:'Months since signup',axis:{labelAngle:0}},y:{field:'Cohort',type:'ordinal',sort:['Jan 2026','Feb 2026','Mar 2026','Apr 2026','May 2026','Jun 2026'],title:'Signup cohort'},tooltip:[{field:'Cohort',type:'nominal',title:'Signup cohort'},{field:'Age',type:'ordinal',title:'Month age'},{field:'Eligible Cohort Users',type:'quantitative',format:',.0f',title:'Cohort users'},{field:'Retained Users',type:'quantitative',format:',.0f'},{field:'Retention Rate',type:'quantitative',format:'.1%'}]},
  layer:[{mark:{type:'rect',cornerRadius:6,stroke:'#161D44',strokeWidth:6},encoding:{color:{field:'Retention Rate',type:'quantitative',scale:{domain:[0,1],range:['#27345E','#BCECF7']},legend:{title:'Retention',format:'.0%',orient:'bottom'}}}},{mark:{type:'text',font:'Segoe UI',fontSize:26,fontWeight:'bold'},encoding:{text:{field:'Retention Rate',type:'quantitative',format:'.0%'},color:{condition:{test:'datum["Retention Rate"] > 0.5',value:'#101534'},value:'#FFFFFF'}}}],
  config:{view:{stroke:null},axis:{labelColor:'#E7EEFF',titleColor:'#E7EEFF',labelFont:'Segoe UI',titleFont:'Segoe UI',labelFontSize:22,titleFontSize:24,grid:false,domain:false,ticks:false,labelPadding:14,titlePadding:20},legend:{labelColor:'#E7EEFF',titleColor:'#E7EEFF',labelFontSize:18,titleFontSize:20}}
};
write(path.join(root,'templates/deneb/vibe-retention-heatmap.json'), spec);
const scaffoldPageRoot = path.join(report,'definition/pages');
const pageIndex = read(path.join(scaffoldPageRoot,'pages.json'));
const firstPage = read(path.join(scaffoldPageRoot,pageIndex.pageOrder[0],'page.json'));
const pageIds = brief.pages.map((p,i)=>i===0?firstPage.name:id(p.name));
write(path.join(scaffoldPageRoot,'pages.json'),{...pageIndex,pageOrder:pageIds,activePageName:pageIds[0]});
function bounds(layout,p) {
  const [a,b,c,d]=layout.grid.regions[p.region], m=layout.canvas.margin;
  const cw=(layout.canvas.width-2*m)/12,ch=(layout.canvas.height-2*m)/12;
  let x=m+(a-1)*cw,y=m+(b-1)*ch,w=(c-a)*cw,h=(d-b)*ch;
  const gap=layout.canvas.gutter;
  if(p.of){if(w>h){w/=p.of;x+=(p.slot-1)*w;}else{h/=p.of;y+=(p.slot-1)*h;}}
  return {x:Math.ceil((x+gap/2)/8)*8,y:Math.ceil((y+gap/2)/8)*8,width:Math.floor((w-gap)/8)*8,height:Math.floor((h-gap)/8)*8};
}
function container(title,transparent=false) {
  return {background:entry({show:lit(!transparent),color:fill('#161D44'),transparency:lit(0)}),border:entry({show:lit(false)}),padding:entry(Object.fromEntries(['top','bottom','left','right'].map(k=>[k,lit(16)]))),visualHeader:entry({show:lit(false)}),title:entry({show:lit(!!title),text:lit(title||''),fontColor:fill('#FFFFFF'),fontSize:lit(22)}),general:entry({altText:lit(title||'Report navigation or explanatory text')})};
}
brief.pages.forEach((p,i)=>{
  const pageDir=path.join(scaffoldPageRoot,pageIds[i]);
  write(path.join(pageDir,'page.json'),{...firstPage,name:pageIds[i],displayName:p.name,width:p.layout_contract.canvas.width,height:p.layout_contract.canvas.height,objects:{background:entry({color:fill('#10103E'),transparency:lit(0),image:{image:{name:lit('template_1.jpg'),url:{expr:{ResourcePackageItem:{PackageName:'RegisteredResources',PackageType:1,ItemName:'template_1.jpg'}}},scaling:lit('Fit')}}})}});
  p.layout_contract.placements.forEach((placement,j)=>{
    let type=placement.kind==='tableEx'?'pivotTable':placement.kind==='Deneb'?'deneb7E15AEF80B9E4D4F8E12924291ECE89A':placement.kind;
    const position={...bounds(p.layout_contract,placement),z:j,tabOrder:j};
    const visual={visualType:type,objects:{},visualContainerObjects:container(placement.purpose),drillFilterOtherVisuals:true};
    const set=(obj,props,selector)=>{
      if(selector && visual.objects[obj]) visual.objects[obj].push(...entry(props,selector));
      else visual.objects[obj]=entry(props,selector);
    };
    if(type==='textbox') {
      visual.visualContainerObjects=container('',true);
      visual.visualContainerObjects.padding=entry(Object.fromEntries(['top','bottom','left','right'].map(k=>[k,lit(0)])));
      set('general',{paragraphs:[{textRuns:[{value:placement.text,textStyle:{fontFamily:'Segoe UI Semibold',fontSize:placement.id==='page_title'?'38px':'26px',color:placement.id==='page_title'?'#FFFFFF':'#F5C769'}}]}]});
    } else if(type==='pageNavigator') {
      visual.visualContainerObjects=container('',true);
      set('text',{fontSize:lit(22),fontColor:fill('#FFFFFF'),show:lit(true)},{id:'default'});
      set('text',{fontSize:lit(22),fontColor:fill('#10103E'),show:lit(true)},{id:'selected'});
      set('fill',{show:lit(true),fillColor:fill('#FF7A45'),transparency:lit(0)},{id:'selected'});
      set('layout',{orientation:lit('0'),rowCount:lit(1),columnCount:lit(3),cellPadding:lit(16)});
    } else {
      let queryState={};
      const bind=placement.field_bindings;
      if(type==='slicer') {
        queryState.Values={projections:[proj(bind)]};
        set('data',{mode:lit('Dropdown')});
        set('header',{show:lit(true),text:lit(placement.id==='segment_slicer'?'Segment':i===2?'Signup cohort':'Activity month'),fontColor:fill('#FFFFFF'),textSize:lit(14)});
        set('items',{fontColor:fill('#FFFFFF'),background:fill('#161D44'),textSize:lit(14)});
        visual.visualContainerObjects.title=entry({show:lit(false)});
      } else if(type==='cardVisual') {
        queryState.Data={projections:[proj(bind)]};
        const color=colors[bind]||'#61D8F5';
        const valueSize=Math.min(28,Math.max(12,Math.floor(p.layout_contract.canvas.height*0.028)));
        const labelSize=Math.min(14,Math.max(8,Math.floor(valueSize*0.55)));
        position.height=34+Math.ceil(valueSize*1.5)+Math.ceil(Math.max(labelSize,12)*1.5);
        set('value',{fontSize:lit(valueSize),fontColor:fill(color),labelDisplayUnits:lit('0')},{id:'default'});
        set('label',{show:lit(true),fontSize:lit(labelSize),fontColor:fill('#FFFFFF')},{id:'default'});
        set('padding',{paddingUniform:lit(8)},{id:'default'});
        set('spacing',{verticalSpacing:lit(2)},{id:'default'});
        visual.visualContainerObjects.padding=entry(Object.fromEntries(['top','bottom','left','right'].map(k=>[k,lit(8)])),{id:'default'});
        set('fillCustom',{show:lit(true),fillColor:fill('#161D44'),transparency:lit(0)},{id:'default'});
        set('layout',{paddingUniform:lit(0)},{id:'default'});
        visual.visualContainerObjects.title=entry({show:lit(false)});
      } else if(type==='pivotTable') {
        const projections=bind.map(proj);
        queryState.Rows={projections:projections.filter(v=>v.field.Column)};
        queryState.Values={projections:projections.filter(v=>v.field.Measure)};
        set('columnHeaders',{fontSize:lit(18),fontColor:fill('#FFFFFF'),backColor:fill('#212B53'),columnAdjustment:lit('growToFit'),autoSizeColumnWidth:lit(true)});
        set('rowHeaders',{fontSize:lit(18),fontColor:fill('#FFFFFF'),backColor:fill('#161D44'),stepped:lit(false)});
        set('values',{fontSize:lit(18),fontColorPrimary:fill('#FFFFFF'),fontColorSecondary:fill('#FFFFFF'),backColorPrimary:fill('#161D44'),backColorSecondary:fill('#212B53')});
        set('subTotals',{rowSubtotals:lit(false),columnSubtotals:lit(false)});
        visual.visualContainerObjects.stylePreset=entry({name:lit('None')});
      } else if(type.startsWith('deneb')) {
        const heatBindings=['Users[SignupCohort]','CohortAge[Age]','CohortActivity[Eligible Cohort Users]','CohortActivity[Retained Users]','CohortActivity[Retention Rate]'];
        queryState.dataset={projections:heatBindings.map(proj)};
        set('vega',{jsonSpec:lit(JSON.stringify(spec)),jsonConfig:lit('{}'),provider:lit('vegaLite'),enableSelection:lit(false),enableTooltips:lit(true)});
        visual.drillFilterOtherVisuals=false;
      } else {
        queryState.Category={projections:[{...proj(bind.Category),active:true}]};
        queryState.Y={projections:[proj(bind.Y)]};
        set('dataPoint',{defaultColor:fill(colors[bind.Y]||'#61D8F5')});
        set('categoryAxis',{labelColor:fill('#FFFFFF'),fontSize:lit(18)});
        set('valueAxis',{labelColor:fill('#FFFFFF'),fontSize:lit(18)});
      }
      visual.query={queryState};
      if(['lineChart','clusteredBarChart','clusteredColumnChart'].includes(type)) {
        const chronological=type==='lineChart'||placement.sort_policy==='category_asc';
        visual.query.sortDefinition={sort:[{field:proj(chronological?bind.Category:bind.Y).field,direction:chronological?'Ascending':'Descending'}],isDefaultSort:true};
      }
    }
    write(path.join(pageDir,'visuals',id(p.name+':'+placement.id),'visual.json'),{$schema:'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.9.0/schema.json',name:id(p.name+':'+placement.id),position,visual});
    if(type==='cardVisual') {
      const full=bounds(p.layout_contract,placement), sparkId=id(p.name+':'+placement.id+':trend');
      const category=proj('Date[MonthStart]');
      write(path.join(pageDir,'visuals',sparkId,'visual.json'),{$schema:'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.9.0/schema.json',name:sparkId,position:{x:full.x,y:full.y+position.height+8,width:full.width,height:full.height-position.height-8,z:j+100,tabOrder:j+100},visual:{visualType:'lineChart',query:{queryState:{Category:{projections:[{...category,active:true}]},Y:{projections:[proj(placement.field_bindings)]}},sortDefinition:{sort:[{field:category.field,direction:'Ascending'}],isDefaultSort:true}},objects:{dataPoint:entry({defaultColor:fill(colors[placement.field_bindings]||'#61D8F5')}),categoryAxis:entry({show:lit(false)}),valueAxis:entry({show:lit(false)})},visualContainerObjects:container('',false),drillFilterOtherVisuals:true}});
    }
  });
});
const registered=path.join(report,'StaticResources/RegisteredResources');
fs.mkdirSync(registered,{recursive:true});
fs.copyFileSync(path.join(root,'templates/backgrounds/template_1.jpg'),path.join(registered,'template_1.jpg'));
const themeName='VibeNavy-736fa192.json';
const theme={name:themeName,dataColors:['#FF7A45','#61D8F5','#80E2BA','#C5A8FF','#F5C769'],foreground:'#FFFFFF',foregroundNeutralSecondary:'#D3DEF6',foregroundNeutralTertiary:'#C4D0EF',background:'#161D44',backgroundLight:'#27345E',backgroundNeutral:'#212B53',tableAccent:'#61D8F5',textClasses:{label:{fontFace:'Segoe UI',fontSize:18,color:'#FFFFFF'},title:{fontFace:'Segoe UI Semibold',fontSize:22,color:'#FFFFFF'},callout:{fontFace:'Segoe UI',fontSize:46,color:'#FFFFFF'},header:{fontFace:'Segoe UI Semibold',fontSize:20,color:'#FFFFFF'}},visualStyles:{'*':{'*':{visualHeader:[{show:false}],outspacePane:[{backgroundColor:{solid:{color:'#161D44'}},foregroundColor:{solid:{color:'#FFFFFF'}}}],filterCard:[{$id:'Available',backgroundColor:{solid:{color:'#212B53'}},foregroundColor:{solid:{color:'#FFFFFF'}}},{$id:'Applied',backgroundColor:{solid:{color:'#27345E'}},foregroundColor:{solid:{color:'#FFFFFF'}}}]}}}};
theme.textClasses.callout.fontSize=28;
delete theme.visualStyles['*']['*'].outspacePane;
delete theme.visualStyles['*']['*'].filterCard;
for(const pageId of pageIds) {
  const file=path.join(scaffoldPageRoot,pageId,'page.json'), page=read(file);
  page.objects.outspacePane=entry({backgroundColor:fill('#161D44'),foregroundColor:fill('#FFFFFF'),inputBoxColor:fill('#212B53')});
  page.objects.filterCard=['Available','Applied'].map(state=>({selector:{id:state},properties:{backgroundColor:fill('#212B53'),foregroundColor:fill('#FFFFFF'),inputBoxColor:fill('#161D44')}}));
  write(file,page);
}
write(path.join(registered,themeName),theme);
write(path.join(root,'templates/themes/vibe-navy.json'),theme);
const reportJson=read(path.join(report,'definition/report.json'));
reportJson.themeCollection.customTheme={name:themeName,type:'RegisteredResources',reportVersionAtImport:reportJson.themeCollection.baseTheme.reportVersionAtImport};
reportJson.resourcePackages=reportJson.resourcePackages.filter(p=>p.name!=='RegisteredResources');
reportJson.resourcePackages.push({name:'RegisteredResources',type:'RegisteredResources',items:[{name:themeName,path:themeName,type:'CustomTheme'},{name:'template_1.jpg',path:'template_1.jpg',type:'Image'}]});
reportJson.publicCustomVisuals=['deneb7E15AEF80B9E4D4F8E12924291ECE89A'];
write(path.join(report,'definition/report.json'),reportJson);
console.log('Authored 3 pages from the approved brief; native visual bindings and Deneb specification persisted.');
