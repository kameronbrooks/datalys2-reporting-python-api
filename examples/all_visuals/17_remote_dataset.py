"""Remote datasets (dl2 0.5+).

Datasets declared with a URL are fetched in the browser at load time — nothing
is embedded in the HTML. Visuals show a loading placeholder, then fill in;
refresh_interval re-fetches and swaps data in place without losing view state.

This script compiles offline (nothing is fetched at build time). The URLs
below point at the dl2 viewer repo's test fixtures on the CDN so the report
actually loads data when opened with internet access.
"""

from pathlib import Path

# Allow running from a repo checkout without installing dl2-reports.
try:
    import dl2_reports  # noqa: F401
except ModuleNotFoundError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from dl2_reports import Card, DL2Report, Table

OUT = Path(__file__).parent / "output"
OUT.mkdir(exist_ok=True)

FIXTURES = "https://cdn.jsdelivr.net/gh/kameronbrooks/datalys2-reporting@latest"

report = DL2Report(
    title="Remote Datasets Showcase",
    description="Data fetched by the browser at load time.",
    compress_visuals=False,
)

# JSON rows nested inside a wrapper object -> extract reaches them.
report.add_remote_dataset(
    "remote_json",
    f"{FIXTURES}/sample-remote-nested.json",
    extract="result.rows",
    refresh_interval=300,
)

# CSV: header row becomes the columns; declared dtypes drive date conversion.
report.add_remote_dataset(
    "remote_csv",
    f"{FIXTURES}/sample-remote.csv",
    response_type="csv",
)

# Derived datasets work with remote sources: derivation waits for the fetch
# and re-runs on every refresh.
report.add_derived_dataset("remote_filtered", "remote_json")

page = report.add_page("Remote data")
page.add_row().add(Card(
    content_type="md",
    text=(
        "These visuals load their data **after** the report opens. "
        "Offline, they show an inline error instead — the rest of the report "
        "is unaffected."
    ),
))
row = page.add_row()
row.add(Table("remote_json", title="Remote JSON (extract='result.rows')"))
row.add(Table("remote_csv", title="Remote CSV"))
page.add_row().add(Table("remote_filtered", title="Derived from a remote source"))

out_file = OUT / "17_remote_dataset.html"
report.save(str(out_file))
print(f"wrote {out_file}")
