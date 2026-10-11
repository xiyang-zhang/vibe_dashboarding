"""Run the repository's setup checks without duplicating implementations."""
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[4]
for arguments in (["-m", "unittest", "discover", "-s", "tests", "-v"], ["scripts/validate_project.py"]):
    subprocess.run([sys.executable, *arguments], cwd=root, check=True)
