import argparse
from pathlib import Path
from previewlib import ROOT, DISCLOSURE, generate, load, validate, reconcile, write_json

def main():
    p = argparse.ArgumentParser(description="Generate deterministic synthetic event data")
    p.add_argument("--config", type=Path, default=ROOT/"config/dashboard.yaml")
    p.add_argument("--schema", type=Path, default=ROOT/"config/schema.yaml")
    p.add_argument("--output", type=Path, default=ROOT/"data/mock")
    p.add_argument("--docs", type=Path, default=ROOT/"docs")
    p.add_argument("--parquet", action="store_true")
    args = p.parse_args()
    cfg, schema = load(args.config), load(args.schema)
    tables = generate(cfg["generation"])
    errors = validate(tables, schema)
    if errors:
        raise ValueError(errors)
    args.output.mkdir(parents=True, exist_ok=True)
    for name, df in tables.items():
        df.to_csv(args.output/f"{name}.csv", index=False)
        if args.parquet:
            df.to_parquet(args.output/f"{name}.parquet", index=False)
    totals, buckets = reconcile(tables, cfg["generation"]["granularity"])
    buckets.to_csv(args.output/"reconciliation_by_period.csv")
    write_json(args.output/"manifest.json", {"disclosure": DISCLOSURE, "generation": cfg["generation"], "rows": {k: len(v) for k, v in tables.items()}})
    write_json(args.docs/"reconciliation.json", totals)
    args.docs.mkdir(parents=True, exist_ok=True)
    lines = ["# Data dictionary", "", DISCLOSURE, "", "| Table | Column | Type | Nullable | Key |", "| --- | --- | --- | --- | --- |"]
    for name, spec in schema["tables"].items():
        for col, dtype in spec["columns"].items():
            lines.append(f"| {name} | {col} | {dtype} | {col in spec.get('nullable', [])} | {'PK' if col == spec['primary_key'] else ''} |")
    (args.docs/"data_dictionary.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    print(f"PASS: generated {sum(len(t) for t in tables.values())} rows; reconciliation={totals['additive_reconciliation']}")

if __name__ == "__main__":
    main()
