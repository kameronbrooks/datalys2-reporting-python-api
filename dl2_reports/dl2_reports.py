from __future__ import annotations
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
import json
import datetime
import gzip
import base64
import html

from .utilities import analytics



class DL2Report:
    class ReportTreeComponent:
        """
        Base class for components in the report tree.
        """
        def __init__(self):
            self.parent: Optional[Any] = None

        def get_report(self) -> Optional[DL2Report]:
            """
            Gets the parent DL2Report instance.
            
            :param self: Description
            :return: Description
            :rtype: DL2Report | None
            """
            if self.parent is None:
                raise ValueError("Component is not attached to a report.")
            if hasattr(self.parent, "get_report"):
                return self.parent.get_report()
            
            return None
    
    class Visual(ReportTreeComponent):
        def __init__(self, type: str, dataset_id: Optional[str] = None, **kwargs):
            super().__init__()
            self.type = type
            self.dataset_id = dataset_id
            self.other_elements: List[Dict[str, Any]] = []
            self.props = kwargs
        


        def add_element(self, type: str, **kwargs) -> DL2Report.Visual:
            """
            Adds a visual element (annotation) to the visual.
            
            Args:
                type: The type of element ('trend', 'xAxis', 'yAxis', 'marker', 'label').
                **kwargs: Additional properties for the element:
                    * **color** (str): Color of the element.
                    * **line_style** (str): 'solid', 'dashed', or 'dotted'.
                    * **line_width** (int): Width of the line.
                    * **label** (str): Text label for the element.
                    * **coefficients** (List[float]): For 'trend' type (e.g., [intercept, slope]).
                    * **value** (any): For 'xAxis', 'yAxis', 'marker', 'label' types.
                    * **size** (int): For 'marker' type.
                    * **shape** (str): For 'marker' type ('circle', 'square', 'triangle').
            
            Returns:
                DL2Report.Visual: The Visual instance.
            """
            element = {"visual_element_type": type}
            element.update(kwargs)
            self.other_elements.append(element)
            return self
        
        def add_trend(self, coefficients: (List[float] | int | None) = None, **kwargs) -> DL2Report.Visual:
            """
            Adds a trend line element to the visual.
            
            Args:
                coefficients: List of coefficients for the trend line (e.g., [intercept, slope]).
                **kwargs: Additional properties for the trend element:
                    * **color** (str): Color of the trend line.
                    * **line_style** (str): 'solid', 'dashed', or 'dotted'.
                    * **line_width** (int): Width of the line.
            
            Returns:
                DL2Report.Visual: The Visual instance.
            """

            # TODO: Only allow trends for certain visual types?
            if self.type not in ["line", "scatter", "bar"]:
                raise ValueError("Trend elements can only be added to line, scatter, or bar visuals.")

            element: Dict[str, Any] = {"visual_element_type": "trend", "coefficients": []}

            if coefficients is None or isinstance(coefficients, int):
                # Auto-calculate coefficients if not provided
                # if coefficients is an int, treat that as the degree
                degree = (coefficients-1) if isinstance(coefficients, int) else 1

                # get the columns from the visual props
                x_column = self.props.get("x_column", None)
                y_column = self.props.get("y_column", None)

                if x_column is None or y_column is None:
                    raise ValueError("Cannot auto-calculate trend coefficients without x_column and y_column in visual props.")
                
                report = self.get_report()
                if report is None:
                    raise ValueError("Cannot auto-calculate trend coefficients without a parent report.")
                
                dataset_id = self.dataset_id
                if dataset_id is None or dataset_id not in report.datasets:
                    raise ValueError("Cannot auto-calculate trend coefficients without a valid dataset_id in the visual.")
                
                dataset: Dict[str, Any] = report.datasets[dataset_id]
                df = dataset.get("_df", None)

                if df is None or not isinstance(df, pd.DataFrame):
                    raise ValueError("Cannot auto-calculate trend coefficients without the original DataFrame in the dataset.")
                
                x = df[x_column].to_numpy()
                y = df[y_column].to_numpy()

                coefficients = analytics.calculate_trend_coefficients(x, y, degree=degree)

            
            element["coefficients"] = coefficients
            
            element.update(kwargs)
            self.other_elements.append(element)
            return self

        def to_dict(self) -> Dict[str, Any]:
            d: Dict[str, Any] = {
                "type": self.type,
                "elementType": "visual"
            }
            if self.dataset_id:
                d["datasetId"] = self.dataset_id
            
            if self.other_elements:
                d["otherElements"] = [DL2Report._camel_case_dict(e) for e in self.other_elements]
            
            # Convert snake_case keys to camelCase for the JSON
            for k, v in self.props.items():
                camel_k = "".join(word.capitalize() if i > 0 else word for i, word in enumerate(k.split("_")))
                if isinstance(v, dict):
                    d[camel_k] = DL2Report._camel_case_dict(v)
                elif isinstance(v, list):
                    d[camel_k] = [DL2Report._camel_case_dict(i) if isinstance(i, dict) else i for i in v]
                else:
                    d[camel_k] = v
            return d

    class Layout(ReportTreeComponent):
        def __init__(self, direction: str = "row", **kwargs):
            """
            Initializes a new Layout.
            
            Args:
                direction: The direction of the layout ('row' or 'column').
                **kwargs: Additional properties for the layout:
                    * **height** (int): Height of the layout in pixels.
                    * **gap** (int): Gap between children in pixels.
                    * **padding** (int): Padding in pixels.
                    * **margin** (int): Margin in pixels.
                    * **border** (bool/str): CSS border or boolean to enable default.
                    * **shadow** (bool/str): CSS box-shadow or boolean to enable default.
                    * **flex** (int): Flex grow value.
            """
            super().__init__()
            self.type = "layout"
            self.direction = direction
            self.children: List[DL2Report.Layout | DL2Report.Visual] = []
            self.props = kwargs

        def add_visual(self, type: str, dataset_id: Optional[str] = None, **kwargs) -> DL2Report.Visual:
            """
            Adds a generic visual to the layout.
            
            Args:
                type: The type of visual (e.g., 'line', 'area', 'bar').
                dataset_id: The ID of the dataset to use for the visual.
                **kwargs: Additional properties for the visual:
                    * **padding** (int): Padding in pixels.
                    * **margin** (int): Margin in pixels.
                    * **border** (bool/str): CSS border or boolean to enable default.
                    * **shadow** (bool/str): CSS box-shadow or boolean to enable default.
                    * **flex** (int): Flex grow value.
                    * **modal_id** (str): The ID of a modal to open when the expand icon is clicked.
            
            Returns:
                DL2Report.Visual: The Visual instance.
            """
            visual = DL2Report.Visual(type, dataset_id, **kwargs)
            visual.parent = self
            self.children.append(visual)
            return visual
        
        def add_layout(self, direction: str = "row", **kwargs) -> DL2Report.Layout:
            """
            Adds a nested layout to the current layout.
            
            Args:
                direction: The direction of the nested layout ('row' or 'column').
                **kwargs: Additional properties for the layout.
            
            Returns:
                DL2Report.Layout: The Layout instance.
            """
            layout = DL2Report.Layout(direction, **kwargs)
            layout.parent = self
            self.children.append(layout)
            return layout

        def add_kpi(
            self,
            dataset_id: str,
            value_column: str | int,
            title: Optional[str] = None,
            comparison_column: str | int | None = None,
            comparison_row_index: int | None = None,
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
        ) -> DL2Report.Visual:
            """Adds a KPI visual to the layout.

            This matches the KPI schema documented in `DOCUMENTATION.md`.

            Args:
                dataset_id: The ID of the dataset.
                value_column: Column for the main value.
                title: Optional title for the KPI card.
                comparison_column: Column for the comparison value (e.g., yesterday).
                comparison_row_index: Index of the row to use for comparison. Supports negative indices.
                row_index: Index of the row in the dataset to display. Supports negative indices.
                format: Formatting style. One of: 'number', 'currency', 'percent', 'date'.
                currency_symbol: Symbol for currency (default '$' in the viewer).
                good_direction: Which direction is considered "good" ('higher' or 'lower').
                breach_value: Value that triggers a breach indicator.
                warning_value: Value that triggers a warning indicator.
                description: Optional description text displayed at the bottom.
                width: Optional width for the KPI card.
                height: Optional height for the KPI card.
                **kwargs: Additional properties (including common visual properties like
                    padding, margin, border, shadow, flex, modal_id).

            Returns:
                DL2Report.Visual: The Visual instance.
            """
            visual_kwargs = dict(kwargs)

            # Required KPI properties
            visual_kwargs["value_column"] = value_column

            # Optional KPI properties
            if title is not None:
                visual_kwargs["title"] = title
            if description is not None:
                visual_kwargs["description"] = description
            if comparison_column is not None:
                visual_kwargs["comparison_column"] = comparison_column
            if comparison_row_index is not None:
                visual_kwargs["comparison_row_index"] = comparison_row_index
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
        ) -> DL2Report.Visual:
            """
            Adds a table visual to the layout.
            
            Args:
                dataset_id: The ID of the dataset.
                title: Optional title for the table.
                columns: Optional array of column names to display.
                page_size: Number of rows per page.
                table_style: Visual style of the table ('plain', 'bordered', 'alternating').
                show_search: Whether to show the search bar.
                **kwargs: Additional properties:
                    * **padding**, **margin**, **border**, **shadow**, **flex**, **modal_id**: Common visual properties.
            
            Returns:
                DL2Report.Visual: The Visual instance.
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

        def add_card(self, title: str | None, text: str, **kwargs) -> DL2Report.Visual:
            """
            Adds a card visual with static or computed text.
            
            Args:
                title: Optional title of the card (supports {{expr}}).
                text: The text content of the card (supports {{expr}}).
                **kwargs: Additional properties:
                    * **padding**, **margin**, **border**, **shadow**, **flex**, **modal_id**: Common visual properties.
            
            Returns:
                DL2Report.Visual: The Visual instance.
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
        ) -> DL2Report.Visual:
            """
            Adds a pie chart visual.
            
            Args:
                dataset_id: The ID of the dataset.
                category_column: Column for slice labels.
                value_column: Column for slice size.
                inner_radius: For donut chart style.
                show_legend: Whether to show the legend.
                **kwargs: Additional properties:
                    * **padding**, **margin**, **border**, **shadow**, **flex**, **modal_id**: Common visual properties.
            
            Returns:
                DL2Report.Visual: The Visual instance.
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
        ) -> DL2Report.Visual:
            """
            Adds a bar chart visual (clustered or stacked).
            
            Args:
                dataset_id: The ID of the dataset.
                x_column: Column for X-axis categories.
                y_columns: The list of columns for the Y-axis.
                stacked: Whether to stack the bars.
                x_axis_label: Label for X-axis.
                y_axis_label: Label for Y-axis.
                show_legend: Whether to show the legend.
                show_labels: Whether to show value labels on bars.
                horizontal: Whether to display bars horizontally.
                **kwargs: Additional properties:
                    * **padding**, **margin**, **border**, **shadow**, **flex**, **modal_id**: Common visual properties.
            
            Returns:
                DL2Report.Visual: The Visual instance.
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
        ) -> DL2Report.Visual:
            """
            Adds a scatter plot visual.
            
            Args:
                dataset_id: The ID of the dataset.
                x_column: Column for X-axis values (numeric).
                y_column: Column for Y-axis values (numeric).
                category_column: Optional column for coloring points by category.
                show_trendline: Whether to show a linear regression trendline.
                show_correlation: Whether to show correlation stats.
                point_size: Size of the data points.
                x_axis_label: Label for X-axis.
                y_axis_label: Label for Y-axis.
                    * **padding**, **margin**, **border**, **shadow**, **flex**, **modal_id**: Common visual properties.
            
            Returns:
                DL2Report.Visual: The Visual instance.
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
        ) -> DL2Report.Visual:
            """
            Adds a line chart visual.
            
            Args:
                dataset_id: The ID of the dataset.
                x_column: Column for X-axis values (usually time or category).
                y_columns: The column(s) for the Y-axis.
                smooth: Whether to use a smooth curve instead of straight lines.
                show_legend: Whether to show the legend.
                show_labels: Whether to show value labels on points.
                min_y: Optional minimum Y-axis value.
                max_y: Optional maximum Y-axis value.
                colors: Array of colors for the lines.
                x_axis_label: Label for X-axis.
                y_axis_label: Label for Y-axis.
                **kwargs: Additional properties:
                    * **padding**, **margin**, **border**, **shadow**, **flex**, **modal_id**: Common visual properties.
            
            Returns:
                DL2Report.Visual: The Visual instance.
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
        ) -> DL2Report.Visual:
            """
            Adds a checklist visual.
            
            Args:
                dataset_id: The ID of the dataset.
                status_column: Column name containing boolean/truthy value for completion.
                warning_column: Column name containing a date to check against.
                warning_threshold: Days before due date to trigger warning.
                columns: Optional array of column names to display.
                page_size: Number of rows per page.
                show_search: Whether to show the search bar.
                **kwargs: Additional properties:
                    * **padding**, **margin**, **border**, **shadow**, **flex**, **modal_id**: Common visual properties.
            
            Returns:
                DL2Report.Visual: The Visual instance.
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
        ) -> DL2Report.Visual:
            """
            Adds a histogram visual.
            
            Args:
                dataset_id: The ID of the dataset.
                column: Column containing the numerical values to bin.
                bins: Number of bins to divide the data into.
                color: Color of the bars.
                show_labels: Whether to show count labels on top of bars.
                x_axis_label: Label for X-axis.
                y_axis_label: Label for Y-axis.
                **kwargs: Additional properties:
                    * **padding**, **margin**, **border**, **shadow**, **flex**, **modal_id**: Common visual properties.
            
            Returns:
                DL2Report.Visual: The Visual instance.
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
        ) -> DL2Report.Visual:
            """
            Adds a heatmap visual.
            
            Args:
                dataset_id: The ID of the dataset.
                x_column: Column for X-axis categories.
                y_column: Column for Y-axis categories.
                value_column: Column for the heat value.
                show_cell_labels: Whether to show the value text inside cells.
                min_value: Optional minimum value for color scale.
                max_value: Optional maximum value for color scale.
                color: Color scheme (e.g., "Viridis") or array of colors.
                x_axis_label: Label for X-axis.
                y_axis_label: Label for Y-axis.
                **kwargs: Additional properties:
                    * **padding**, **margin**, **border**, **shadow**, **flex**, **modal_id**: Common visual properties.
            
            Returns:
                DL2Report.Visual: The Visual instance.
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
        ) -> DL2Report.Visual:
            """
            Adds a box plot visual.
            
            Args:
                dataset_id: The ID of the dataset.
                data_column: Raw numerical values to calculate box stats (Data Mode).
                category_column: Column to group data by (Data Mode) or label rows (Pre-calc Mode).
                min_column/q1_column/median_column/q3_column/max_column/mean_column: Pre-calc Mode columns.
                direction: 'vertical' or 'horizontal'.
                show_outliers: Whether to show outliers.
                color: Fill color or D3 scheme name.
                x_axis_label: Label for X-axis.
                y_axis_label: Label for Y-axis.
                **kwargs: Additional properties:
                    * **padding**, **margin**, **border**, **shadow**, **flex**, **modal_id**: Common visual properties.
            
            Returns:
                DL2Report.Visual: The Visual instance.
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

        def add_modal_button(self, modal_id: str, button_label: str, **kwargs) -> DL2Report.Visual:
            """
            Adds a button that triggers a modal.
            
            Args:
                modal_id: The ID of the modal to open.
                button_label: The text to display on the button.
                **kwargs: Additional properties for the button:
                    * **padding**, **margin**, **border**, **shadow**, **flex**: Common visual properties.
            
            Returns:
                DL2Report.Visual: The Visual instance.
            """
            return self.add_visual("modal", id=modal_id, button_label=button_label, **kwargs)

        def to_dict(self) -> Dict[str, Any]:
            """
            Converts the layout and its children to a dictionary.
            
            Returns:
                Dict[str, Any]: A dictionary representation of the layout.
            """
            d: Dict[str, Any] = {
                "type": "layout",
                "direction": self.direction,
                "children": [c.to_dict() for c in self.children]
            }
            for k, v in self.props.items():
                camel_k = "".join(word.capitalize() if i > 0 else word for i, word in enumerate(k.split("_")))
                if isinstance(v, dict):
                    d[camel_k] = DL2Report._camel_case_dict(v)
                elif isinstance(v, list):
                    d[camel_k] = [DL2Report._camel_case_dict(i) if isinstance(i, dict) else i for i in v]
                else:
                    d[camel_k] = v
            return d

    class Page(ReportTreeComponent):
        def __init__(self, title: str, description: Optional[str] = None):
            """
            Initializes a new Page.
            
            Args:
                title: The title of the page.
                description: Optional description of the page.
            """
            super().__init__()
            self.title = title
            self.description = description
            self.rows: List[DL2Report.Layout] = []

        def add_row(self, direction: str = "row", **kwargs) -> DL2Report.Layout:
            """
            Adds a new layout row to the page.
            
            Args:
                direction: The direction of the row ('row' or 'column').
                **kwargs: Additional properties for the layout.
            
            Returns:
                DL2Report.Layout: The Layout instance.
            """
            row = DL2Report.Layout(direction, **kwargs)
            row.parent = self
            self.rows.append(row)
            return row

        def to_dict(self) -> Dict[str, Any]:
            """
            Converts the page to a dictionary.
            
            Returns:
                Dict[str, Any]: A dictionary representation of the page.
            """
            d: Dict[str, Any] = {
                "title": self.title,
                "rows": [r.to_dict() for r in self.rows]
            }
            if self.description:
                d["description"] = self.description
            return d

    class Modal(ReportTreeComponent):
        def __init__(self, id: str, title: str, description: Optional[str] = None):
            """
            Initializes a new Modal.
            
            Args:
                id: Unique identifier for the modal.
                title: The title of the modal.
                description: Optional description of the modal.
            """
            super().__init__()
            self.id = id
            self.title = title
            self.description = description
            self.rows: List[DL2Report.Layout] = []

        def add_row(self, direction: str = "row", **kwargs) -> DL2Report.Layout:
            """
            Adds a new layout row to the modal.
            
            Args:
                direction: The direction of the row ('row' or 'column').
                **kwargs: Additional properties for the layout.
            
            Returns:
                DL2Report.Layout: The Layout instance.
            """
            row = DL2Report.Layout(direction, **kwargs)
            row.parent = self
            self.rows.append(row)
            return row

        def to_dict(self) -> Dict[str, Any]:
            """
            Converts the modal to a dictionary.
            
            Returns:
                Dict[str, Any]: A dictionary representation of the modal.
            """
            d: Dict[str, Any] = {
                "id": self.id,
                "title": self.title,
                "rows": [r.to_dict() for r in self.rows]
            }
            if self.description:
                d["description"] = self.description
            return d

    @staticmethod
    def _camel_case_dict(d: Dict[str, Any]) -> Dict[str, Any]:
        new_d = {}
        for k, v in d.items():
            camel_k = "".join(word.capitalize() if i > 0 else word for i, word in enumerate(k.split("_")))
            if isinstance(v, dict):
                new_d[camel_k] = DL2Report._camel_case_dict(v)
            elif isinstance(v, list):
                new_d[camel_k] = [DL2Report._camel_case_dict(i) if isinstance(i, dict) else i for i in v]
            else:
                new_d[camel_k] = v
        return new_d
    
    @staticmethod
    def _make_dataset_serializable(dataset: Dict[str, Any]) -> Dict[str, Any]:
        serializable_dataset = dataset.copy()
        if "_df" in serializable_dataset:
            del serializable_dataset["_df"]
        return serializable_dataset

    def __init__(self, title: str, description: str = "", author: str = ""):
        """
        Initializes a new DL2Report.
        
        Args:
            title: The title of the report.
            description: A brief description of the report.
            author: The author of the report.
        """
        self.title = title
        self.description = description
        self.author = author
        self.pages: List[DL2Report.Page] = []
        self.modals: List[DL2Report.Modal] = []
        self.datasets: Dict[str, Dict[str, Any]] = {}
        self.compressed_datasets: Dict[str, str] = {}
        self.css_url = "https://cdn.jsdelivr.net/gh/kameronbrooks/datalys2-reporting@latest/dist/dl2-style.css"
        self.js_url = "https://cdn.jsdelivr.net/gh/kameronbrooks/datalys2-reporting@latest/dist/datalys2-reports.min.js"
        self.meta_tags: Dict[str, str] = {}

    def get_report(self) -> DL2Report:
        """
        Gets the parent DL2Report instance.
        
        :param self: Description
        :return: Description
        :rtype: DL2Report | None
        """
        return self

    def add_df(self, 
               name: str, 
               df: pd.DataFrame, 
               format: str = "records", 
               compress: bool = False,
               timestamp_format: str = "iso"
            ) -> DL2Report:
        """
        Adds a DataFrame to the report.
        
        Args:
            name: Name of the dataset.
            df: The DataFrame to add.
            format: Data format ('records' or 'table').
            compress: Whether to compress the data using gzip.
            timestamp_format: Format for datetime columns ('iso' or 'epoch').
        
        Returns:
            DL2Report: The DL2Report instance.
            """
        columns = df.columns.tolist()
        dtypes = []
        for dtype in df.dtypes:
            if pd.api.types.is_numeric_dtype(dtype):
                dtypes.append("number")
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                dtypes.append("date")
            else:
                dtypes.append("string")

        # Handle datetime formatting
        for col in df.columns:
            if not pd.api.types.is_datetime64_any_dtype(df[col]):
                continue

            # Normalize to UTC so tz-aware and naive datetimes behave consistently.
            # Naive datetimes are treated as UTC.
            series_utc = pd.to_datetime(df[col], utc=True)

            if timestamp_format == "iso":
                df[col] = series_utc.dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            elif timestamp_format == "epoch":
                # pandas stores datetimes in ns; convert to whole seconds.
                df[col] = (series_utc.astype("int64") // 1_000_000_000)
            else:
                raise ValueError("Invalid timestamp_format. Use 'iso' or 'epoch'.")

        if format == "records":
            data = df.to_dict(orient="records")
        else:
            data = df.values.tolist()

        dataset_entry = {
            "id": name,
            "format": format,
            "columns": columns,
            "dtypes": dtypes,
            "data": data,
            "_df": df  # Store original DataFrame for reference
        }

        if compress:
            # Convert data to JSON string, then gzip, then base64
            json_data = json.dumps(data)
            compressed = gzip.compress(json_data.encode("utf-8"))
            b64_data = base64.b64encode(compressed).decode("utf-8")
            
            script_id = f"compressed-data-{name}"
            self.compressed_datasets[script_id] = b64_data
            
            dataset_entry["compression"] = "gzip"
            dataset_entry["compressedData"] = script_id
            dataset_entry["data"] = []
            
            # Enable GC for compressed data
            self.set_meta("gc-compressed-data", "true")

        self.datasets[name] = dataset_entry
        return self

    def add_page(self, title: str, description: Optional[str] = None) -> DL2Report.Page:
        page = DL2Report.Page(title, description)
        page.parent = self
        self.pages.append(page)
        return page

    def add_modal(self, id: str, title: str, description: Optional[str] = None) -> DL2Report.Modal:
        """
        Adds a modal to the report.
        
        Args:
            id: Unique identifier for the modal.
            title: The title displayed in the modal header.
            description: Optional description text.
        
        Returns:
            DL2Report.Modal: The Modal instance.
        """
        modal = DL2Report.Modal(id, title, description)
        modal.parent = self
        self.modals.append(modal)
        return modal

    def set_meta(self, name: str, content: str) -> DL2Report:
        """
        Sets a meta tag for the report.
        
        Args:
            name: The name of the meta tag.
            content: The content of the meta tag.
        
        Returns:
            DL2Report: The DL2Report instance.
        """
        self.meta_tags[name] = content
        return self

    def compile(self) -> str:
        """
        Compiles the report into a single HTML string.
        
        Returns:
            str: The compiled HTML string.
        """
        report_data = {
            "pages": [p.to_dict() for p in self.pages],
            "datasets": {name: self._make_dataset_serializable(ds) for name, ds in self.datasets.items()}
        }
        if self.modals:
            report_data["modals"] = [m.to_dict() for m in self.modals]
            
        report_data_json = json.dumps(report_data, indent=4)

        meta_html = ""
        for name, content in self.meta_tags.items():
            meta_html += f'    <meta name="{name}" content="{content}">\n'

        compressed_scripts = ""
        for script_id, b64_data in self.compressed_datasets.items():
            compressed_scripts += f'    <script id="{script_id}" type="text/b64-gzip">{b64_data}</script>\n'

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    <meta name="dl-version" content="0.2.2">
    <meta name="description" content="{self.description}">
    <meta name="author" content="{self.author}">
    <meta name="last-updated" content="{datetime.datetime.now().isoformat()}">
{meta_html}
    <link rel="stylesheet" href="{self.css_url}">
</head>
<body>
{compressed_scripts}
    <div id="root"></div>
    <script id="report-data" type="application/json">
{report_data_json}
    </script>
    <script src="{self.js_url}"></script>
</body>
</html>"""
        return html

    def save(self, filename: str):
        """
        Saves the compiled report to a file.
        
        Args:
            filename: The path to the file to save.
        """
        with open(filename, "w", encoding="utf-8") as f:
            f.write(self.compile())

    def show(self, height: int = 800):
        """
        Displays the report directly in a Jupyter Notebook cell using an iframe.
        
        Args:
            height: The height of the iframe in pixels (default 800).
        """
        try:
            from IPython.display import IFrame
            import base64
            
            # Use a data URI with IFrame to avoid the UserWarning and local file issues.
            # This is the most portable way to embed the HTML.
            b64_html = base64.b64encode(self.compile().encode('utf-8')).decode('utf-8')
            data_uri = f"data:text/html;base64,{b64_html}"
            return IFrame(data_uri, width="100%", height=height)
        except ImportError:
            # Fallback for environments without IPython
            print("IPython not found. Save the report to an HTML file to view it.")

    def _repr_html_(self):
        """
        Enables automatic rendering in Jupyter Notebooks when the report object is the last line of a cell.
        
        Returns:
            str: An iframe string containing the report.
        """
        # We use srcdoc here because _repr_html_ must return a string.
        # This might still trigger a warning in some environments, but it's the standard way for _repr_html_.
        escaped_html = html.escape(self.compile())
        return f'<iframe srcdoc="{escaped_html}" width="100%" height="800px" style="border:none;"></iframe>'
