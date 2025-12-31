from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..serialization import camel_case_dict, snake_to_camel
from .base import ReportTreeComponent
from .visual import Visual


class Layout(ReportTreeComponent):
    def __init__(self, direction: str = "row", **kwargs):
        """Initializes a new layout container.

        Layouts can contain other layouts and/or visuals and control how children
        are arranged.

        Args:
            direction: Layout direction ('row', 'column', or 'grid' depending on viewer support).
            **kwargs: Additional layout properties (serialized to JSON):
                padding, margin, border, shadow, flex, height, gap, columns, etc.
        """
        super().__init__()
        self.type = "layout"
        self.direction = direction
        self.children: List[Layout | Visual] = []
        self.props = kwargs

    def add_visual(self, type: str, dataset_id: Optional[str] = None, **kwargs) -> Visual:
        """Adds a generic visual to the layout.

        Args:
            type: Visual type (e.g., 'kpi', 'table', 'line', 'scatter').
            dataset_id: Dataset id to bind to this visual.
            **kwargs: Visual properties (serialized to JSON). Common ones include:
                padding, margin, border, shadow, flex, modal_id.

        Returns:
            The created :class:`~dl2_reports.components.visual.Visual` instance.
        """
        visual = Visual(type, dataset_id, **kwargs)
        visual.parent = self
        self.children.append(visual)
        return visual

    def add_layout(self, direction: str = "row", **kwargs) -> Layout:
        """Adds a nested layout to this layout.

        Args:
            direction: Layout direction for the nested layout.
            **kwargs: Additional layout properties.

        Returns:
            The created nested :class:`~dl2_reports.components.layout.Layout`.
        """
        layout = Layout(direction, **kwargs)
        layout.parent = self
        self.children.append(layout)
        return layout

    # Visual helpers
    def add_kpi(
        self,
        dataset_id: str,
        value_column: str | int,
        title: Optional[str] = None,
        comparison_column: str | int | None = None,
        comparison_row_index: int | None = None,
        comparison_text: str | None = None,
        row_index: int | None = None,
        format: str | None = None,
        currency_symbol: str | None = None,
        good_direction: str | None = None,
        breach_value: float | int | None = None,
        warning_value: float | int | None = None,
        description: Optional[str] = None,
        width: int | None = None,
        height: int | None = None,
        **kwargs,
    ) -> Visual:
        """Adds a KPI visual.

        Matches the KPI schema documented in `DOCUMENTATION.md`.

        Args:
            dataset_id: The dataset id.
            value_column: Column for the main KPI value.
            title: Optional KPI card title.
            comparison_column: Column for the comparison value.
            comparison_row_index: Row index to use for comparison (supports negative indices).
            comparison_text: The comparison text to show alongside the comparison value. Ex. ("Last Month", "Yesterday", etc.).
            row_index: Row index to display (supports negative indices).
            format: 'number', 'currency', 'percent', or 'date'.
            currency_symbol: Currency symbol (viewer default is '$').
            good_direction: Which direction is "good" ('higher' or 'lower').
            breach_value: Value that triggers a breach indicator.
            warning_value: Value that triggers a warning indicator.
            description: Optional description text.
            width: Optional width.
            height: Optional height.
            **kwargs: Additional common visual properties.

        Returns:
            The created KPI visual.
        """
        visual_kwargs = dict(kwargs)
        visual_kwargs["value_column"] = value_column

        if title is not None:
            visual_kwargs["title"] = title
        if description is not None:
            visual_kwargs["description"] = description
        if comparison_column is not None:
            visual_kwargs["comparison_column"] = comparison_column
        if comparison_row_index is not None:
            visual_kwargs["comparison_row_index"] = comparison_row_index
        if comparison_text is not None:
            visual_kwargs["comparison_text"] = comparison_text
        if row_index is not None:
            visual_kwargs["row_index"] = row_index
        if format is not None:
            visual_kwargs["format"] = format
        if currency_symbol is not None:
            visual_kwargs["currency_symbol"] = currency_symbol
        if good_direction is not None:
            visual_kwargs["good_direction"] = good_direction
        if breach_value is not None:
            visual_kwargs["breach_value"] = breach_value
        if warning_value is not None:
            visual_kwargs["warning_value"] = warning_value
        if width is not None:
            visual_kwargs["width"] = width
        if height is not None:
            visual_kwargs["height"] = height

        return self.add_visual("kpi", dataset_id, **visual_kwargs)

    def add_table(
        self,
        dataset_id: str,
        title: Optional[str] = None,
        columns: Optional[List[str]] = None,
        page_size: int | None = None,
        table_style: str | None = None,
        show_search: bool | None = None,
        **kwargs,
    ) -> Visual:
        """Adds a table visual.

        Args:
            dataset_id: The dataset id.
            title: Optional table title.
            columns: Optional list of columns to display.
            page_size: Rows per page.
            table_style: 'plain', 'bordered', or 'alternating'.
            show_search: Whether to show the search box.
            **kwargs: Additional common visual properties.

        Returns:
            The created table visual.
        """
        visual_kwargs = dict(kwargs)
        if title is not None:
            visual_kwargs["title"] = title
        if columns is not None:
            visual_kwargs["columns"] = columns
        if page_size is not None:
            visual_kwargs["page_size"] = page_size
        if table_style is not None:
            visual_kwargs["table_style"] = table_style
        if show_search is not None:
            visual_kwargs["show_search"] = show_search
        return self.add_visual("table", dataset_id, **visual_kwargs)

    def add_card(self, title: str | None, text: str, **kwargs) -> Visual:
        """Adds a card visual.

        Args:
            title: Optional title (supports template syntax in the viewer).
            text: Main card text (supports template syntax in the viewer).
            **kwargs: Additional common visual properties.

        Returns:
            The created card visual.
        """
        visual_kwargs = dict(kwargs)
        if title is not None:
            visual_kwargs["title"] = title
        visual_kwargs["text"] = text
        return self.add_visual("card", None, **visual_kwargs)

    def add_pie(
        self,
        dataset_id: str,
        category_column: str | int,
        value_column: str | int,
        inner_radius: int | None = None,
        show_legend: bool | None = None,
        **kwargs,
    ) -> Visual:
        """Adds a pie/donut chart visual.

        Args:
            dataset_id: The dataset id.
            category_column: Column for slice labels.
            value_column: Column for slice values.
            inner_radius: Inner radius for donut styling.
            show_legend: Whether to show the legend.
            **kwargs: Additional common visual properties.

        Returns:
            The created pie visual.
        """
        visual_kwargs = dict(kwargs)
        visual_kwargs["category_column"] = category_column
        visual_kwargs["value_column"] = value_column
        if inner_radius is not None:
            visual_kwargs["inner_radius"] = inner_radius
        if show_legend is not None:
            visual_kwargs["show_legend"] = show_legend
        return self.add_visual("pie", dataset_id, **visual_kwargs)

    def add_bar(
        self,
        dataset_id: str,
        x_column: str | int,
        y_columns: List[str],
        stacked: bool = False,
        x_axis_label: Optional[str] = None,
        y_axis_label: Optional[str] = None,
        show_legend: bool | None = None,
        show_labels: bool | None = None,
        horizontal: bool | None = None,
        **kwargs,
    ) -> Visual:
        """Adds a clustered or stacked bar chart visual.

        Args:
            dataset_id: The dataset id.
            x_column: Column for X-axis categories.
            y_columns: Series columns for Y values.
            stacked: If True, uses stacked bars; otherwise clustered.
            x_axis_label: Optional X-axis label.
            y_axis_label: Optional Y-axis label.
            show_legend: Whether to show the legend.
            show_labels: Whether to show value labels.
            horizontal: Whether to render bars horizontally (viewer-dependent).
            **kwargs: Additional common visual properties.

        Returns:
            The created bar visual.
        """
        type = "stackedBar" if stacked else "clusteredBar"
        visual_kwargs = dict(kwargs)
        visual_kwargs["x_column"] = x_column
        visual_kwargs["y_columns"] = y_columns
        if x_axis_label is not None:
            visual_kwargs["x_axis_label"] = x_axis_label
        if y_axis_label is not None:
            visual_kwargs["y_axis_label"] = y_axis_label
        if show_legend is not None:
            visual_kwargs["show_legend"] = show_legend
        if show_labels is not None:
            visual_kwargs["show_labels"] = show_labels
        if horizontal is not None:
            visual_kwargs["horizontal"] = horizontal
        return self.add_visual(type, dataset_id, **visual_kwargs)

    def add_scatter(
        self,
        dataset_id: str,
        x_column: str | int,
        y_column: str | int,
        category_column: str | int | None = None,
        show_trendline: bool | None = None,
        show_correlation: bool | None = None,
        point_size: int | None = None,
        x_axis_label: Optional[str] = None,
        y_axis_label: Optional[str] = None,
        **kwargs,
    ) -> Visual:
        """Adds a scatter plot visual.

        Args:
            dataset_id: The dataset id.
            x_column: Column for numeric X values.
            y_column: Column for numeric Y values.
            category_column: Optional column for coloring points by category.
            show_trendline: Whether to show a trendline.
            show_correlation: Whether to show correlation stats.
            point_size: Point size.
            x_axis_label: Optional X-axis label.
            y_axis_label: Optional Y-axis label.
            **kwargs: Additional common visual properties.

        Returns:
            The created scatter visual.
        """
        visual_kwargs = dict(kwargs)
        visual_kwargs["x_column"] = x_column
        visual_kwargs["y_column"] = y_column
        if category_column is not None:
            visual_kwargs["category_column"] = category_column
        if show_trendline is not None:
            visual_kwargs["show_trendline"] = show_trendline
        if show_correlation is not None:
            visual_kwargs["show_correlation"] = show_correlation
        if point_size is not None:
            visual_kwargs["point_size"] = point_size
        if x_axis_label is not None:
            visual_kwargs["x_axis_label"] = x_axis_label
        if y_axis_label is not None:
            visual_kwargs["y_axis_label"] = y_axis_label
        return self.add_visual("scatter", dataset_id, **visual_kwargs)

    def add_line(
        self,
        dataset_id: str,
        x_column: str | int,
        y_columns: List[str] | str,
        smooth: bool | None = None,
        show_legend: bool | None = None,
        show_labels: bool | None = None,
        min_y: float | int | None = None,
        max_y: float | int | None = None,
        colors: Optional[List[str]] = None,
        x_axis_label: Optional[str] = None,
        y_axis_label: Optional[str] = None,
        **kwargs,
    ) -> Visual:
        """Adds a line chart visual.

        Args:
            dataset_id: The dataset id.
            x_column: Column for X values (time or category).
            y_columns: Column(s) for Y series.
            smooth: Whether to render smooth curves.
            show_legend: Whether to show the legend.
            show_labels: Whether to show value labels.
            min_y: Optional minimum Y.
            max_y: Optional maximum Y.
            colors: Optional list of series colors.
            x_axis_label: Optional X-axis label.
            y_axis_label: Optional Y-axis label.
            **kwargs: Additional common visual properties.

        Returns:
            The created line visual.
        """
        visual_kwargs = dict(kwargs)
        visual_kwargs["x_column"] = x_column
        visual_kwargs["y_columns"] = y_columns
        if smooth is not None:
            visual_kwargs["smooth"] = smooth
        if show_legend is not None:
            visual_kwargs["show_legend"] = show_legend
        if show_labels is not None:
            visual_kwargs["show_labels"] = show_labels
        if min_y is not None:
            visual_kwargs["min_y"] = min_y
        if max_y is not None:
            visual_kwargs["max_y"] = max_y
        if colors is not None:
            visual_kwargs["colors"] = colors
        if x_axis_label is not None:
            visual_kwargs["x_axis_label"] = x_axis_label
        if y_axis_label is not None:
            visual_kwargs["y_axis_label"] = y_axis_label
        return self.add_visual("line", dataset_id, **visual_kwargs)

    def add_checklist(
        self,
        dataset_id: str,
        status_column: str,
        warning_column: Optional[str] = None,
        warning_threshold: int | None = None,
        columns: Optional[List[str]] = None,
        page_size: int | None = None,
        show_search: bool | None = None,
        **kwargs,
    ) -> Visual:
        """Adds a checklist visual.

        Args:
            dataset_id: The dataset id.
            status_column: Column containing a truthy completion value.
            warning_column: Optional date column to evaluate for warnings.
            warning_threshold: Days before due date to trigger warning.
            columns: Optional subset of columns to display.
            page_size: Rows per page.
            show_search: Whether to show the search box.
            **kwargs: Additional common visual properties.

        Returns:
            The created checklist visual.
        """
        visual_kwargs = dict(kwargs)
        visual_kwargs["status_column"] = status_column
        if warning_column is not None:
            visual_kwargs["warning_column"] = warning_column
        if warning_threshold is not None:
            visual_kwargs["warning_threshold"] = warning_threshold
        if columns is not None:
            visual_kwargs["columns"] = columns
        if page_size is not None:
            visual_kwargs["page_size"] = page_size
        if show_search is not None:
            visual_kwargs["show_search"] = show_search
        return self.add_visual("checklist", dataset_id, **visual_kwargs)

    def add_histogram(
        self,
        dataset_id: str,
        column: str | int,
        bins: int | None = None,
        color: Optional[str] = None,
        show_labels: bool | None = None,
        x_axis_label: Optional[str] = None,
        y_axis_label: Optional[str] = None,
        **kwargs,
    ) -> Visual:
        """Adds a histogram visual.

        Args:
            dataset_id: The dataset id.
            column: Numeric column to bin.
            bins: Number of bins.
            color: Bar color.
            show_labels: Whether to show count labels.
            x_axis_label: Optional X-axis label.
            y_axis_label: Optional Y-axis label.
            **kwargs: Additional common visual properties.

        Returns:
            The created histogram visual.
        """
        visual_kwargs = dict(kwargs)
        visual_kwargs["column"] = column
        if bins is not None:
            visual_kwargs["bins"] = bins
        if color is not None:
            visual_kwargs["color"] = color
        if show_labels is not None:
            visual_kwargs["show_labels"] = show_labels
        if x_axis_label is not None:
            visual_kwargs["x_axis_label"] = x_axis_label
        if y_axis_label is not None:
            visual_kwargs["y_axis_label"] = y_axis_label
        return self.add_visual("histogram", dataset_id, **visual_kwargs)

    def add_heatmap(
        self,
        dataset_id: str,
        x_column: str | int,
        y_column: str | int,
        value_column: str | int,
        show_cell_labels: bool | None = None,
        min_value: float | int | None = None,
        max_value: float | int | None = None,
        color: str | List[str] | None = None,
        x_axis_label: Optional[str] = None,
        y_axis_label: Optional[str] = None,
        **kwargs,
    ) -> Visual:
        """Adds a heatmap visual.

        Args:
            dataset_id: The dataset id.
            x_column: Column for X categories.
            y_column: Column for Y categories.
            value_column: Column for cell values.
            show_cell_labels: Whether to show values inside cells.
            min_value: Optional minimum for the color scale.
            max_value: Optional maximum for the color scale.
            color: D3 interpolator name (e.g., 'Viridis') or custom colors.
            x_axis_label: Optional X-axis label.
            y_axis_label: Optional Y-axis label.
            **kwargs: Additional common visual properties.

        Returns:
            The created heatmap visual.
        """
        visual_kwargs = dict(kwargs)
        visual_kwargs["x_column"] = x_column
        visual_kwargs["y_column"] = y_column
        visual_kwargs["value_column"] = value_column
        if show_cell_labels is not None:
            visual_kwargs["show_cell_labels"] = show_cell_labels
        if min_value is not None:
            visual_kwargs["min_value"] = min_value
        if max_value is not None:
            visual_kwargs["max_value"] = max_value
        if color is not None:
            visual_kwargs["color"] = color
        if x_axis_label is not None:
            visual_kwargs["x_axis_label"] = x_axis_label
        if y_axis_label is not None:
            visual_kwargs["y_axis_label"] = y_axis_label
        return self.add_visual("heatmap", dataset_id, **visual_kwargs)

    def add_boxplot(
        self,
        dataset_id: str,
        data_column: str | int | None = None,
        category_column: str | int | None = None,
        min_column: str | int | None = None,
        q1_column: str | int | None = None,
        median_column: str | int | None = None,
        q3_column: str | int | None = None,
        max_column: str | int | None = None,
        mean_column: str | int | None = None,
        direction: str | None = None,
        show_outliers: bool | None = None,
        color: str | List[str] | None = None,
        x_axis_label: Optional[str] = None,
        y_axis_label: Optional[str] = None,
        **kwargs,
    ) -> Visual:
        """Adds a box plot visual.

        Supports two modes:
        - Data mode: provide `data_column` (and optional `category_column`).
        - Pre-calculated mode: provide min/q1/median/q3/max (and optional mean).

        Args:
            dataset_id: The dataset id.
            data_column: Raw values column (data mode).
            category_column: Grouping/label column.
            min_column/q1_column/median_column/q3_column/max_column/mean_column: Pre-calc columns.
            direction: 'vertical' or 'horizontal'.
            show_outliers: Whether to show outliers.
            color: Fill color or scheme.
            x_axis_label: Optional X-axis label.
            y_axis_label: Optional Y-axis label.
            **kwargs: Additional common visual properties.

        Returns:
            The created boxplot visual.
        """
        visual_kwargs = dict(kwargs)
        if data_column is not None:
            visual_kwargs["data_column"] = data_column
        if category_column is not None:
            visual_kwargs["category_column"] = category_column
        if min_column is not None:
            visual_kwargs["min_column"] = min_column
        if q1_column is not None:
            visual_kwargs["q1_column"] = q1_column
        if median_column is not None:
            visual_kwargs["median_column"] = median_column
        if q3_column is not None:
            visual_kwargs["q3_column"] = q3_column
        if max_column is not None:
            visual_kwargs["max_column"] = max_column
        if mean_column is not None:
            visual_kwargs["mean_column"] = mean_column
        if direction is not None:
            visual_kwargs["direction"] = direction
        if show_outliers is not None:
            visual_kwargs["show_outliers"] = show_outliers
        if color is not None:
            visual_kwargs["color"] = color
        if x_axis_label is not None:
            visual_kwargs["x_axis_label"] = x_axis_label
        if y_axis_label is not None:
            visual_kwargs["y_axis_label"] = y_axis_label
        return self.add_visual("boxplot", dataset_id, **visual_kwargs)

    def add_modal_button(self, modal_id: str, button_label: str, **kwargs) -> Visual:
        """Adds a modal trigger button.

        Args:
            modal_id: The global modal id to open.
            button_label: Button label text.
            **kwargs: Additional common visual properties.

        Returns:
            The created modal trigger visual.
        """
        return self.add_visual("modal", id=modal_id, button_label=button_label, **kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes this layout and its children to a JSON-ready dict."""
        d: Dict[str, Any] = {
            "type": "layout",
            "direction": self.direction,
            "children": [c.to_dict() for c in self.children],
        }
        for k, v in self.props.items():
            camel_k = snake_to_camel(k)
            if isinstance(v, dict):
                d[camel_k] = camel_case_dict(v)
            elif isinstance(v, list):
                d[camel_k] = [camel_case_dict(i) if isinstance(i, dict) else i for i in v]
            else:
                d[camel_k] = v
        return d
