"""Compatibility shim — the migration tool now ships inside the package.

Run it as:
    python -m dl2_reports.migrate PATH [--write]
"""

import sys

from dl2_reports.migrate import main

if __name__ == "__main__":
    sys.exit(main())
