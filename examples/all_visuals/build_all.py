"""Runs every numbered example in this folder and writes the HTML files to
./output. Run from anywhere:

    python examples/all_visuals/build_all.py
"""

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).parent

# Make the repo checkout importable when dl2_reports isn't pip-installed.
repo_root = HERE.parents[1]
if (repo_root / "dl2_reports").is_dir():
    sys.path.insert(0, str(repo_root))

failures = []
for script in sorted(HERE.glob("[0-9][0-9]_*.py")):
    print(f"-- {script.name}")
    try:
        runpy.run_path(str(script), run_name="__main__")
    except Exception as exc:  # keep going so one bad example doesn't hide the rest
        failures.append((script.name, exc))
        print(f"   FAILED: {exc}")

if failures:
    print(f"\n{len(failures)} example(s) failed.")
    sys.exit(1)
print("\nAll examples built. Open the files in examples/all_visuals/output/ in a browser.")
