# Datalys2 Reporting Python API — Documentation

**Package version 0.8.0 · targets dl2 viewer 0.5.0**

`dl2-reports` builds self-contained interactive HTML reports from pandas DataFrames.
This documentation is organized so that **every visual type and every feature has its
own page**.

- New here? Start with **[Getting Started](getting-started.md)**.
- Looking for the raw JSON config the viewer consumes (no Python)? See the
  **[datalys2-reporting viewer repo](https://github.com/kameronbrooks/datalys2-reporting)** —
  it documents the full JSON spec.
- Runnable one-file demos for every visual live in
  [examples/all_visuals/](../examples/all_visuals/).

> Version tags like *(dl2 0.3+)* refer to the **viewer** (JS) version a feature
> requires; the compiled HTML pins `dl-version 0.5.0`.

## Visuals

One page per visual type. Every visual also accepts the
[common visual properties](features/common-props.md).

| Visual | Type | Page | Example |
|--------|------|------|---------|
| KPI card | `kpi` | [visuals/kpi.md](visuals/kpi.md) | [02_kpi.py](../examples/all_visuals/02_kpi.py) |
| Card (text / md / html) | `card` | [visuals/card.md](visuals/card.md) | [03_card.py](../examples/all_visuals/03_card.py) |
| Table | `table` | [visuals/table.md](visuals/table.md) | [04_table.py](../examples/all_visuals/04_table.py) |
| Checklist | `checklist` | [visuals/checklist.md](visuals/checklist.md) | [05_checklist.py](../examples/all_visuals/05_checklist.py) |
| Pie / Donut | `pie` | [visuals/pie.md](visuals/pie.md) | [06_pie.py](../examples/all_visuals/06_pie.py) |
| Bar (clustered / stacked) | `clusteredBar` / `stackedBar` | [visuals/bar.md](visuals/bar.md) | [07_bar.py](../examples/all_visuals/07_bar.py) |
| Line chart | `line` | [visuals/line.md](visuals/line.md) | [08_line.py](../examples/all_visuals/08_line.py) |
| Area chart | `area` | [visuals/area.md](visuals/area.md) | [09_area.py](../examples/all_visuals/09_area.py) |
| Scatter plot | `scatter` | [visuals/scatter.md](visuals/scatter.md) | [10_scatter.py](../examples/all_visuals/10_scatter.py) |
| Histogram | `histogram` | [visuals/histogram.md](visuals/histogram.md) | [11_histogram.py](../examples/all_visuals/11_histogram.py) |
| Heatmap | `heatmap` | [visuals/heatmap.md](visuals/heatmap.md) | [12_heatmap.py](../examples/all_visuals/12_heatmap.py) |
| Box plot | `boxplot` | [visuals/boxplot.md](visuals/boxplot.md) | [13_boxplot.py](../examples/all_visuals/13_boxplot.py) |
| Gauge | `gauge` | [visuals/gauge.md](visuals/gauge.md) | [14_gauge.py](../examples/all_visuals/14_gauge.py) |
| Calendar *(dl2 0.5+)* | `calendar` | [visuals/calendar.md](visuals/calendar.md) | [16_calendar.py](../examples/all_visuals/16_calendar.py) |
| Tabs container | `tabs` | [visuals/tabs.md](visuals/tabs.md) | [01_tabs.py](../examples/all_visuals/01_tabs.py) |
| Link | `link` | [visuals/link.md](visuals/link.md) | [15_links_and_modals.py](../examples/all_visuals/15_links_and_modals.py) |
| Modal button | `modal` | [visuals/modal-button.md](visuals/modal-button.md) | [15_links_and_modals.py](../examples/all_visuals/15_links_and_modals.py) |
| Generic visual passthrough | any | [visuals/generic-visual.md](visuals/generic-visual.md) | — |

## Features

| Feature | Page |
|---------|------|
| Common visual properties (`id`, `border`, `filter=`, `extra=`, …) | [features/common-props.md](features/common-props.md) |
| Datasets & compression (`add_df`, dtypes, dates) | [features/datasets.md](features/datasets.md) |
| Report configuration (metadata, `report_id`, CDN, save/compile) | [features/report-configuration.md](features/report-configuration.md) |
| Layouts (rows, columns, grids, gap/wrap/align) | [features/layouts.md](features/layouts.md) |
| Filtering (`filter=`, the `filters` builder module) | [features/filtering.md](features/filtering.md) |
| Aggregation (`aggregate=`, the `aggregates` builder module) | [features/aggregation.md](features/aggregation.md) |
| Formula datasources (`"sales[Amount > 200]"`) *(0.7.0+)* | [features/formula-datasources.md](features/formula-datasources.md) |
| Derived datasets (`add_derived_dataset`) | [features/derived-datasets.md](features/derived-datasets.md) |
| Remote datasets (`add_remote_dataset`) *(dl2 0.5+)* | [features/remote-datasets.md](features/remote-datasets.md) |
| Thresholds (pass/fail coloring) | [features/thresholds.md](features/thresholds.md) |
| Annotations (trend lines, markers, axis lines, labels) | [features/annotations.md](features/annotations.md) |
| Column formatting (`column_formats=`) *(dl2 0.4.1+)* | [features/column-formatting.md](features/column-formatting.md) |
| Conditional formatting (`conditional_formats=`) *(dl2 0.4.1+)* | [features/conditional-formatting.md](features/conditional-formatting.md) |
| Modals (global overlays, row detail modals) | [features/modals.md](features/modals.md) |
| Persistent view state *(dl2 0.4+)* | [features/persistent-view-state.md](features/persistent-view-state.md) |
| Chart image export (PNG/SVG) *(dl2 0.5+)* | [features/chart-export.md](features/chart-export.md) |
| Printing & PDF *(dl2 0.5+)* | [features/printing.md](features/printing.md) |
| Reading values back (`get_value`, `visual.copy`) | [features/reading-values.md](features/reading-values.md) |
| Conditional layout (`on_condition`) | [features/conditional-layout.md](features/conditional-layout.md) |
| Jupyter notebook support (`show`, auto-render) | [features/jupyter.md](features/jupyter.md) |
| Compile-time linting & viewer validation | [features/linting.md](features/linting.md) |
| Migrating to the typed API (codemod) | [features/migration.md](features/migration.md) |

## Internal / design documents

Not user documentation, kept for contributors:
[ARCHITECTURE.md](ARCHITECTURE.md) ·
[JS_CONFIG_REFERENCE_0.3-0.4.md](JS_CONFIG_REFERENCE_0.3-0.4.md) ·
[UPDATE_PLAN.md](UPDATE_PLAN.md) ·
[V2_MIGRATION_PLAN.md](V2_MIGRATION_PLAN.md)
