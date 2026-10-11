import argparse
from pathlib import Path
from previewlib import load, write_json

DENEB = "deneb7E15AEF80B9E4D4F8E12924291ECE89A"

def fields(spec):
    found = set()
    if isinstance(spec, dict):
        if isinstance(spec.get("field"), str):
            found.add(spec["field"])
        for value in spec.values():
            found.update(fields(value))
    elif isinstance(spec, list):
        for value in spec:
            found.update(fields(value))
    return found

def literal(value):
    import json
    text = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return {"expr": {"Literal": {"Value": "'" + text.replace("'", "''") + "'"}}}

def patch(visual, spec):
    if visual["visual"]["visualType"] != DENEB:
        raise ValueError("Require an existing certified Deneb visual")
    if spec.get("data", {}).get("name") != "dataset":
        raise ValueError("Deneb source must be dataset")
    projections = visual["visual"].get("query", {}).get("queryState", {}).get("dataset", {}).get("projections", [])
    bound = {p.get("displayName", p.get("nativeQueryRef")) for p in projections}
    missing = fields(spec) - bound
    if missing:
        raise ValueError(f"Unbound spec fields: {sorted(missing)}")
    import copy
    result = copy.deepcopy(visual)
    result["visual"].setdefault("objects", {})["vega"] = [{"properties": {"jsonSpec": literal(spec), "jsonConfig": literal({})}}]
    return result

def main():
    p = argparse.ArgumentParser(description="Embed spec into an existing bound Deneb visual")
    p.add_argument("visual", type=Path)
    p.add_argument("spec", type=Path)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if args.output.exists():
        raise ValueError("Use a new output path, then review the diff before replacing the baseline")
    write_json(args.output, patch(load(args.visual), load(args.spec)))
    print("Embedded spec; official schema/Power BI rendering validation still required")

if __name__ == "__main__":
    main()
