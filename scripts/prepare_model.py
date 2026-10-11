"""Prepare typed M imports and measure contracts for Microsoft modeling tools."""
import argparse
from pathlib import Path
from previewlib import ROOT, load, write_json

def m_string(value):
    return '"' + value.replace('"', '""') + '"'

def prepare(schema, metrics, data_root):
    types = {"int64": "Int64.Type", "double": "type number", "date": "type date", "string": "type text"}
    tables = []
    for name, spec in schema["tables"].items():
        pairs = ", ".join("{" + m_string(col) + ", " + types[typ] + "}" for col, typ in spec["columns"].items())
        expression = f'let\n    Source = Csv.Document(File.Contents(pMockDataRoot & "/{name}.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),\n    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),\n    Typed = Table.TransformColumnTypes(Headers, {{{pairs}}}, "en-US")\nin\n    Typed'
        tables.append({"name": name, "columns": spec["columns"], "hidden_columns": [spec["primary_key"]] if name != "Date" else [], "partition_mode": "import", "m": expression})
    for rel in schema["relationships"]:
        next(t for t in tables if t["name"] == rel["from_table"])["hidden_columns"].append(rel["from_column"])
    return {"parameter": {"name": "pMockDataRoot", "m": m_string(str(data_root).replace('\\', '/')) + ' meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]'}, "tables": tables, "relationships": schema["relationships"], "measures": metrics["measures"], "date_table": {"table": "Date", "column": "Date", "sort_by": {"MonthName": "Month"}}, "verification": "Authoring inputs only; TMDL, DAX, processing and Desktop NOT VERIFIED"}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data-root", type=Path, default=ROOT/"data/mock")
    p.add_argument("--output", type=Path, default=ROOT/"docs/model_authoring_inputs.json")
    args = p.parse_args()
    write_json(args.output, prepare(load(ROOT/"config/schema.yaml"), load(ROOT/"config/metrics.yaml"), args.data_root))
    print("Prepared model authoring inputs; no semantic model processing performed")

if __name__ == "__main__":
    main()
