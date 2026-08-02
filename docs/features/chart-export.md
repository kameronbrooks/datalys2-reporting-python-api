# Chart image export *(dl2 0.5+)*

Every SVG chart can be right-clicked for **Export PNG** / **Export SVG**. The
props mirror the table's CSV-export API and apply to all 10 chart types:
`line`, `area`, `stackedBar`, `clusteredBar`, `pie`, `scatter`, `histogram`,
`heatmap`, `boxplot`, `gauge`.

```python
from dl2_reports import Line, Pie

page.add_row(
    Line("finance", x_column="Month", y_columns=["Revenue"],
         export_file_name="revenue-trend"),
    Pie("finance", category_column="Month", value_column="Revenue",
        enable_export=False),           # no image export for this one
)
```

## Parameters (on every chart class)

| Parameter | Type | Description |
|-----------|------|-------------|
| `enable_export` | `bool` | Image export in the right-click menu (viewer default `True`). |
| `export_file_name` | `str` | Base file name, no extension. Viewer fallback: visual `title` → dataset id → chart type slug (e.g. `stacked-bar`). |
| `context_menu` | `bool` | The right-click context menu itself (viewer default `True`). Disabling it also disables export. |

## What gets exported

- The chart's `<svg>` element only — the surrounding HTML title, description,
  and legend are not part of the image.
- The theme is resolved into the file: CSS custom properties are baked in and
  the visual's background is carried over, so dark-theme charts stay legible
  on white.
- PNG renders at 2× scale; SVG is standalone. Both work from `file://`.

## Related

- [Table](../visuals/table.md) — the CSV-export API these props mirror.
- [Printing](printing.md) — whole-report print/PDF output.
