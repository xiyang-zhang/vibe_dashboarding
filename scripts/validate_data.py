import argparse
from pathlib import Path
from previewlib import ROOT, load, read_tables, validate, reconcile, write_json, scenario_checks

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", type=Path, default=ROOT/"data/mock")
    p.add_argument("--schema", type=Path, default=ROOT/"config/schema.yaml")
    p.add_argument("--config", type=Path, default=ROOT/"config/dashboard.yaml")
    p.add_argument("--docs", type=Path, default=ROOT/"docs")
    args = p.parse_args()
    schema = load(args.schema)
    tables = read_tables(args.data, schema)
    errors = validate(tables, schema)
    totals = reconcile(tables)[0] if not errors else None
    if totals and not totals["additive_reconciliation"]:
        errors.append("Aggregate reconciliation failed")
    scenario = scenario_checks(tables, load(args.config)["generation"]) if not errors else []
    errors.extend(item["check"] for item in scenario if item["status"] == "FAIL")
    write_json(args.docs/"data_validation.json", {"status": "FAIL" if errors else "PASS", "errors": errors, "totals": totals, "scenario_checks": scenario})
    print("FAIL: " + "; ".join(errors) if errors else "PASS: schema, keys, dates, metric consistency and reconciliation")
    return bool(errors)

if __name__ == "__main__":
    raise SystemExit(main())
