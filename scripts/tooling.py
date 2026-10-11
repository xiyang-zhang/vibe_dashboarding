"""Delegate official Power BI operations without reimplementing the CLI."""
import argparse
import shutil
import subprocess
from pathlib import Path
from previewlib import ROOT

def cli():
    found = shutil.which("powerbi-report-author")
    if not found:
        raise RuntimeError("powerbi-report-author unavailable. Follow installed Microsoft skill setup; no PBIR verification performed.")
    return found

def official(arguments):
    return subprocess.run([cli(), *arguments], check=False).returncode

def doctor():
    for name in ("git", "powerbi-report-author", "az"):
        print(f"{name}: {shutil.which(name) or 'NOT AVAILABLE'}")
    for name in ("powerbi-report-cli", "semantic-model-authoring"):
        path = ROOT/".agents/skills"/name/"SKILL.md"
        print(f"{name}: {'AVAILABLE' if path.exists() else 'MISSING'}")
    paths = [Path(r"C:\Program Files\Microsoft Power BI Desktop\bin\PBIDesktop.exe")]
    print("Desktop executable: " + next((str(p) for p in paths if p.exists()), "NOT DETECTED (Store/custom installs may exist)"))
    print("Desktop refresh/rendering: NOT VERIFIED")

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="mode", required=True)
    sub.add_parser("doctor")
    val = sub.add_parser("validate")
    val.add_argument("report")
    scaffold = sub.add_parser("scaffold")
    scaffold.add_argument("output")
    scaffold.add_argument("--name", required=True)
    args = p.parse_args()
    if args.mode == "doctor":
        doctor()
        return 0
    if args.mode == "validate":
        return official(["validate", args.report])
    if Path(args.output).exists() and any(Path(args.output).iterdir()):
        raise ValueError("Refusing to scaffold into nonempty directory")
    return official(["scaffold", args.output, "--name", args.name])

if __name__ == "__main__":
    raise SystemExit(main())
