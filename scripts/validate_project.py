"""Supplemental local checks; never substitutes for Microsoft validators."""
import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path
from previewlib import ROOT, DISCLOSURE, load, write_json, read_tables, validate

def overlaps(a, b):
    return (a["x"] < b["x"] + b["width"] and b["x"] < a["x"] + a["width"] and a["y"] < b["y"] + b["height"] and b["y"] < a["y"] + a["height"])

def inspect_report(report, config):
    errors, warnings = [], []
    model_path = None
    binding = report/"definition.pbir"
    if not binding.exists():
        return ["Missing definition.pbir"], warnings
    reference = load(binding).get("datasetReference", {})
    if "byPath" in reference:
        model_path = (report/reference["byPath"]["path"]).resolve()
        if not (model_path/"definition.pbism").exists() or not (model_path/"definition/model.tmdl").exists():
            errors.append("Report semantic model reference is missing required files")
    elif "byConnection" not in reference:
        errors.append("Missing report model reference")
    objects = {}
    if model_path:
        for file in (model_path/"definition/tables").glob("*.tmdl"):
            text = file.read_text(encoding="utf-8-sig")
            table = re.search(r"^table (.+)$", text, re.M)
            if table:
                # Only simple local fallback metadata; escaped identifiers require TOM.
                objects[table[1].strip("'")] = set(m[1].strip("'") for m in re.finditer(r"^\s+(?:measure|column) ('(?:[^']|'')*'|[^=\r\n]+?)(?:\s*=|\s*$)", text, re.M))
    names, visual_ids = set(), set()
    pages = list((report/"definition/pages").glob("*/page.json"))
    if not pages:
        errors.append("Report has no page definitions")
    for pagefile in pages:
        page = load(pagefile)
        if page.get("name") in names:
            errors.append("Duplicate page ID")
        names.add(page.get("name"))
        visual_positions = []
        text_evidence = json.dumps(page)
        for vf in (pagefile.parent/"visuals").glob("*/visual.json"):
            v = load(vf)
            text_evidence += json.dumps(v, ensure_ascii=False)
            if v.get("name") in visual_ids:
                errors.append(f"Duplicate visual ID: {vf}")
            visual_ids.add(v.get("name"))
            pos = v.get("position", {})
            if not all(k in pos and isinstance(pos[k], (int, float)) for k in ("x", "y", "width", "height")):
                errors.append(f"Missing/invalid visual bounds: {vf}")
            elif pos["x"] < 0 or pos["y"] < 0 or pos["width"] <= 0 or pos["height"] <= 0 or pos["x"] + pos["width"] > page.get("width", 1280) or pos["y"] + pos["height"] > page.get("height", 720):
                errors.append(f"Visual outside page: {vf}")
            else:
                visual_positions.append((vf, pos))
            visual = v.get("visual", {})
            if not visual.get("visualType"):
                errors.append(f"Missing visual type: {vf}")
            def bindings(value):
                if isinstance(value, dict):
                    for kind in ("Column", "Measure"):
                        field = value.get(kind)
                        if isinstance(field, dict):
                            entity = field.get("Expression", {}).get("SourceRef", {}).get("Entity")
                            prop = field.get("Property")
                            if objects and (entity not in objects or prop not in objects[entity]):
                                errors.append(f"Missing model binding {entity}.{prop}: {vf}")
                    for child in value.values():
                        bindings(child)
                elif isinstance(value, list):
                    for child in value:
                        bindings(child)
            bindings(visual)
        if DISCLOSURE not in text_evidence:
            errors.append(f"Missing synthetic disclosure: {pagefile}")
        for i, (first, a) in enumerate(visual_positions):
            for second, b in visual_positions[i + 1:]:
                if overlaps(a, b):
                    warnings.append(f"Review overlap (may be intentional panel): {first.name}/{first.parent.name}, {second.parent.name}")
    displays = {load(p).get("displayName") for p in pages}
    for required in config.get("required_pages", []):
        if required not in displays:
            errors.append(f"Missing required page: {required}")
    return errors, warnings

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, help="Write validation evidence here, preserving supplied baseline evidence")
    args = parser.parse_args()
    root = args.root.resolve()
    errors, warnings, checks = [], [], {}
    for folder in ("config", "templates", "powerbi"):
        for path in (root/folder).rglob("*"):
            if path.suffix in {".json", ".pbip", ".pbir", ".pbism"}:
                try:
                    load(path)
                except Exception as exc:
                    errors.append(f"{path}: {exc}")
    config = load(root/"config/dashboard.yaml")
    schema = load(root/"config/schema.yaml")
    if config.get("disclosure") != DISCLOSURE:
        errors.append("Missing dashboard disclosure")
    try:
        data_errors = validate(read_tables(root/"data/mock", schema), schema)
        errors.extend(data_errors)
        checks["data"] = "FAIL" if data_errors else "PASS"
    except Exception as exc:
        errors.append(f"Data validation failed: {exc}")
        checks["data"] = "FAIL"
    layout = load(root/"templates/layouts/overview.json")
    panels = layout["panels"]
    for panel in panels:
        if panel["x"] < 0 or panel["y"] < 0 or panel["width"] <= 0 or panel["height"] <= 0 or panel["x"] + panel["width"] > layout["canvas"]["width"] or panel["y"] + panel["height"] > layout["canvas"]["height"]:
            errors.append(f"Layout panel outside canvas: {panel['id']}")
    for i, a in enumerate(panels):
        if any(overlaps(a, b) for b in panels[i + 1:]):
            errors.append(f"Overlapping layout panel: {a['id']}")
    reports = list((root/"powerbi").rglob("*.Report"))
    command = shutil.which("powerbi-report-author")
    for report in reports:
        report_config_path = root/"config"/(report.name.removesuffix(".Report")+".yaml")
        report_config = load(report_config_path) if report_config_path.exists() else config
        report_errors, report_warnings = inspect_report(report, report_config)
        errors.extend(report_errors)
        warnings.extend(report_warnings)
        if command:
            result = subprocess.run([command, "validate", str(report)], capture_output=True, text=True)
            checks[report.relative_to(root).as_posix()+":official-schema"] = "PASS" if result.returncode == 0 else "FAIL"
            if result.returncode:
                errors.append(result.stdout + result.stderr)
        else:
            checks[report.relative_to(root).as_posix()+":official-schema"] = "NOT VERIFIED"
    for project in (root/"powerbi").rglob("*.pbip"):
        for artifact in load(project).get("artifacts", []):
            if "report" in artifact and not (project.parent/artifact["report"]["path"]/"definition.pbir").exists():
                errors.append(f"Invalid PBIP report reference: {project}")
    checks.update({"PBIP reports": "LOCAL CHECKS RUN" if reports else "NOT APPLICABLE — setup only", "TMDL/DAX engine": "NOT VERIFIED", "refresh/connectivity": "NOT VERIFIED", "Desktop/rendering": "NOT VERIFIED", "Deneb official schema/rendering": "NOT VERIFIED"})
    output = {"status": "FAIL" if errors else "PASS", "scope": "repository scaffold and local data checks only", "checks": checks, "errors": errors, "warnings": warnings}
    evidence = args.output or (root/"docs/generated_validation" if reports else root/"docs")
    write_json(evidence/"project_validation.json", output)
    lines = ["# Validation report", "", DISCLOSURE, "", f"Local scaffold status: {output['status']}", "", "| Check | Status |", "| --- | --- |"]
    lines.extend(f"| {k} | {v} |" for k, v in checks.items())
    lines += ["", "Evidence: `python scripts/validate_project.py`; detailed diagnostics in project_validation.json. These are supplemental repository checks. No screenshot, refresh, DAX-engine or Desktop compatibility claim is made."]
    if errors or warnings:
        lines += ["", *[f"- {e}" for e in errors + warnings]]
    (evidence/"validation_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))
    return bool(errors)

if __name__ == "__main__":
    raise SystemExit(main())
