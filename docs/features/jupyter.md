# Jupyter Notebook Support

Reports render directly inside Jupyter environments — classic Jupyter,
JupyterLab, and VS Code notebooks. `IPython` must be installed (it ships with
any Jupyter environment).

## `report.show(height=800)`

Compiles the report and displays it in an IFrame (via a base64 `data:` URI):

```python
report.show()            # 800px tall
report.show(height=1200)
```

If IPython is not available, `show()` prints a hint to save to an HTML file
instead.

## Automatic rendering

A `DL2Report` placed at the end of a cell renders automatically (the class
implements `_repr_html_`, which embeds the compiled report in an
800px-tall `srcdoc` iframe):

```python
report
```

## Notes

- Every call re-compiles the report, so the preview always reflects the
  current state of the tree — build in one cell, preview in the next,
  iterate.
- The notebook preview is the same self-contained HTML as
  [`report.save()`](report-configuration.md#compile--save--show) produces;
  viewer JS/CSS still load from the CDN, so previews need network access
  (or a [`cdn_url`](report-configuration.md#viewer-assets-cdn) override).
- [Persistent view state](persistent-view-state.md) is keyed by report
  identity; iframes get a fresh context, so notebook previews won't disturb
  the saved state of a published copy.

## Related

- [Report configuration](report-configuration.md) — `compile()` / `save()`.
- [examples/](../../examples/) — `test_date_dtypes.ipynb` shows notebook
  usage.
