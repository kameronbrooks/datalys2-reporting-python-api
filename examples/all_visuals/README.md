# All Visuals — Example Gallery

One runnable script per visual type, using the typed component API (v2,
recommended since 0.5.0). Each script writes a standalone HTML report to
`./output/` — open it in a browser.

Build everything at once:

```bash
python examples/all_visuals/build_all.py
```

Or run any single script — each one bootstraps `sys.path` so it works straight
from a repo checkout, no `pip install` needed:

```bash
python examples/all_visuals/01_tabs.py
```

| Script | Visual type(s) | Highlights |
|--------|----------------|------------|
| [01_tabs.py](01_tabs.py) | `tabs` | Incremental `add_tabs`/`add_tab`, declarative `Tabs`/`Tab`, nesting, `default_tab`, persistence, links into tabs |
| [02_kpi.py](02_kpi.py) | `kpi` | Comparisons, currency/percent/hms formats, warning & breach values |
| [03_card.py](03_card.py) | `card` | Plain text, markdown, `{{ ... }}` template expressions |
| [04_table.py](04_table.py) | `table` | Grouping + aggregates, totals, column & conditional formats, row modals, formula datasources |
| [05_checklist.py](05_checklist.py) | `checklist` | Status/warning columns, filter chips, progress bar, `hide_completed` |
| [06_pie.py](06_pie.py) | `pie` | Pie and donut (`inner_radius`) |
| [07_bar.py](07_bar.py) | `clusteredBar`, `stackedBar` | Clustered vs stacked, labels, threshold coloring |
| [08_line.py](08_line.py) | `line` | Multi-series, smoothing, thresholds, annotations (`yAxis`/`xAxis`/`marker`), trend lines |
| [09_area.py](09_area.py) | `area` | Fill opacity, markers, thresholds, fill-only style |
| [10_scatter.py](10_scatter.py) | `scatter` | Category coloring, built-in trendline + correlation, auto-fit `.add_trend()` |
| [11_histogram.py](11_histogram.py) | `histogram` | Bin counts, labels, colors |
| [12_heatmap.py](12_heatmap.py) | `heatmap` | D3 interpolators, custom color ramps, pinned scales |
| [13_boxplot.py](13_boxplot.py) | `boxplot` | Raw-data mode and pre-calculated mode, horizontal orientation |
| [14_gauge.py](14_gauge.py) | `gauge` | Range bands, legend, percent/currency formats |
| [15_links_and_modals.py](15_links_and_modals.py) | `link`, `modal` | Cross-page navigation, modal triggers, row-templated modals |

Notes:

- Examples set `compress_visuals=False` so the generated HTML stays readable.
  Keep the default (`True`) — and `add_df(..., compress=True)` for any real
  dataset — in production reports.
- Reports load the dl2 viewer from the jsdelivr CDN. The **tabs** visual needs
  the viewer build published on 2026-07-20 or later; if tabs (or any visual)
  render as an unknown-type error, hard-refresh (Ctrl+F5) so the browser
  refetches the cached CDN bundle (it caches for up to 7 days).
