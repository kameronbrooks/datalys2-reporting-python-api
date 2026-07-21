from __future__ import annotations

from typing import Any, Dict, List, Optional

import pandas as pd

from ..serialization import RawDict, camel_case_dict, snake_to_camel
from ..utilities import analytics
from .base import ReportTreeComponent

_TREND_ALLOWED_TYPES = frozenset({"line", "area", "scatter", "clusteredBar", "stackedBar", "histogram"})


def _type_models_columns(visual_type: str) -> bool:
    """Whether a visual type models a ``columns`` prop (the viewer only reads it on
    table-like visuals). Unknown/custom types are permitted, matching the lint."""
    from ..lint import _component_registry  # lazy: lint imports this module

    cls = _component_registry().get(visual_type)
    return cls is None or "columns" in cls.known_props()


class Visual(ReportTreeComponent):
    """
    Represents a visualization component in the report.
    """
    def __init__(self, type: str, dataset_id: Optional[str] = None, **kwargs):
        """
        Initializes a new Visual.

        Args:
            type (str): The type of visual (e.g., 'bar', 'line', 'scatter').
            dataset_id (str, optional): The ID of the dataset this visual will use,
                or a pandas-style formula like ``"sales[Amount > 200][['Region']]"``
                (see :mod:`dl2_reports.formulas`). A formula's filter AND-combines
                with an explicit ``filter=``; its ``[[...]]`` projection sets
                ``columns`` (table-like visuals only). Defaults to None.
            **kwargs: Additional properties for the visual (e.g., x_column, y_column).
        """
        super().__init__()
        from ..formulas import and_merge, parse_datasource
        spec = parse_datasource(dataset_id)
        dataset_id = spec.dataset_id
        if spec.filter is not None:
            kwargs["filter"] = and_merge(spec.filter, kwargs.get("filter"))
        if spec.columns is not None:
            if kwargs.get("columns") is not None:
                raise ValueError(
                    f"Ambiguous column selection for '{type}' visual: the datasource "
                    f"formula selects {spec.columns} but an explicit columns= was also "
                    f"provided. Use one or the other."
                )
            if not _type_models_columns(type):
                raise ValueError(
                    f"Column projection ('[[...]]') is not supported for '{type}' "
                    f"visuals; the viewer only reads 'columns' on table-like visuals. "
                    f"Use a filter or a derived dataset instead."
                )
            kwargs["columns"] = spec.columns
        if "filter" in kwargs and kwargs["filter"] is not None:
            from ..filters import validate_filter
            validate_filter(kwargs["filter"])
        if "aggregate" in kwargs and kwargs["aggregate"] is not None:
            from ..aggregates import validate_aggregate
            validate_aggregate(kwargs["aggregate"])
        if kwargs.get("id"):
            # A user-provided id becomes the component's real id (stable ids matter
            # for dl2 0.4 view-state persistence, anchors, and link targets).
            self.id = kwargs["id"]
        self.type = type
        self.dataset_id = dataset_id
        self.other_elements: List[Dict[str, Any]] = []
        self.props = kwargs

    def copy(self) -> Visual:
        """
        Creates a copy of this visual, including its properties and other elements, but with a new unique ID.

        Returns:
            Visual: A new Visual instance with the same properties and elements.
        """
        copied_visual = Visual(self.type, self.dataset_id, **self.props)
        copied_visual.other_elements = [dict(e) for e in self.other_elements]
        return copied_visual

    def add_element(self, type: str, **kwargs) -> Visual:
        """
        Adds a generic visual element (annotation) to the visual.

        Args:
            type (str): The type of element to add.
            **kwargs: Additional properties for the element.

        Returns:
            Visual: The visual instance for method chaining.
        """

        element = {"visual_element_type": type}
        element.update(kwargs)
        self.other_elements.append(element)
        return self
    
    def add_trend(self, coefficients: (List[float] | int | None) = None, **kwargs) -> Visual:
        """
        Adds a trend line element to the visual.

        This method is only supported for 'line', 'area', 'scatter', 'clusteredBar', 'stackedBar',
        and 'histogram' visuals (dl2 0.4.1+ renders trends on all of them).
        If coefficients are not provided, it attempts to auto-calculate them using the visual's dataset
        and properties (specifically x_column and y_column) — so histograms (no y_column) and
        multi-series line/area charts (y_columns) need explicit coefficients.

        Note on units: the viewer evaluates coefficients against the 0-based category index on
        categorical X axes (line, area, bars); numeric axes (scatter, histogram) use real axis units.

        Args:
            coefficients (List[float] | int | None, optional): 
                If a list, these are the polynomial coefficients.
                If an int, it represents the degree of the polynomial to calculate (defaults to 1 if None).
                If None, calculates a linear trend (degree 1).
            **kwargs: Additional properties for the trend line.

        Returns:
            Visual: The visual instance for method chaining.

        Raises:
            ValueError: If the visual type does not support trends.
            ValueError: If auto-calculation fails due to missing props, report, or dataset.
        """

        if self.type not in _TREND_ALLOWED_TYPES:
            raise ValueError(
                "Trend elements can only be added to line, area, scatter, clusteredBar, "
                "stackedBar, or histogram visuals."
            )

        element: Dict[str, Any] = {"visual_element_type": "trend", "coefficients": []}

        if coefficients is None or isinstance(coefficients, int):
            # Auto-calculate coefficients if not provided
            # if coefficients is an int, treat that as the degree
            degree = (coefficients - 1) if isinstance(coefficients, int) else 1

            # get the columns from the visual props
            x_column = self.props.get("x_column", None)
            y_column = self.props.get("y_column", None)

            if x_column is None or y_column is None:
                raise ValueError(
                    "Cannot auto-calculate trend coefficients without x_column and y_column in visual props."
                )

            report = self.get_report()
            if report is None:
                raise ValueError("Cannot auto-calculate trend coefficients without a parent report.")

            dataset_id = self.dataset_id
            if dataset_id is None or dataset_id not in report.datasets:
                raise ValueError("Cannot auto-calculate trend coefficients without a valid dataset_id in the visual.")

            dataset: Dict[str, Any] = report.datasets[dataset_id]
            df = dataset.get("_df", None)

            if df is None or not isinstance(df, pd.DataFrame):
                raise ValueError(
                    "Cannot auto-calculate trend coefficients without the original DataFrame in the dataset."
                )

            x = df[x_column].to_numpy()
            y = df[y_column].to_numpy()

            coefficients = analytics.calculate_trend_coefficients(x, y, degree=degree)

        element["coefficients"] = coefficients

        element.update(kwargs)
        self.other_elements.append(element)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the visual to a dictionary for serialization.

        Returns:
            Dict[str, Any]: The dictionary representation of the visual.
        """
        def _serialize_object(v: Any) -> Any:
            if hasattr(v, "to_dict") and callable(getattr(v, "to_dict")):
                return _serialize_object(v.to_dict())
            elif isinstance(v, RawDict):
                # Keys are data (e.g. column names) — serialize them verbatim.
                return {k: _serialize_object(val) for k, val in v.items()}
            elif isinstance(v, dict):
                return {snake_to_camel(k): _serialize_object(val) for k, val in v.items()}
            elif isinstance(v, list):
                return [_serialize_object(i) for i in v]
            else:
                return v

        d: Dict[str, Any] = {
            "type": self.type,
            "elementType": "visual",
            "id": self.id,
        }
        if self.dataset_id:
            d["datasetId"] = self.dataset_id

        if self.other_elements:
            d["otherElements"] = [_serialize_object(e) for e in self.other_elements]

        for k, v in self.props.items():
            camel_k = snake_to_camel(k)
            d[camel_k] = _serialize_object(v)
        return d
    
    def get_value(self) -> Optional[Any]:
        """
        Attempts to retrieve the value represented by this visual from its dataset, if possible.
        This only works for visuals that have a dataset_id and the original DataFrame available in the dataset.
        It also requires that the visual's props include 'row_index' and 'value_column' to identify which value to retrieve.
        Returns:
            The value from the dataset that this visual represents, or None if it cannot be retrieved.
        Raises:
            ValueError: If the visual does not have a dataset_id.
            ValueError: If the visual is not part of a report.
            ValueError: If the dataset_id is not found in the report's datasets.
            ValueError: If the original DataFrame is not available in the dataset.
            ValueError: If 'row_index' or 'value_column' props are missing or invalid.
        """
        if self.dataset_id is None:
            return None

        report = self.get_report()
        if report is None:
            raise ValueError("Cannot get visual value without a parent report.")

        dataset_id = self.dataset_id
        if dataset_id is None or dataset_id not in report.datasets:
            raise ValueError("Cannot get visual value without a valid dataset_id in the visual.")

        dataset: Dict[str, Any] = report.datasets[dataset_id]
        df = dataset.get("_df", None)

        if df is None or not isinstance(df, pd.DataFrame):
            raise ValueError(
                "Cannot get visual value without the original DataFrame in the dataset."
            )

        if "row_index" in self.props and "value_column" in self.props:
            return report.get_value(self.dataset_id, self.props["value_column"], self.props["row_index"])
        
        else:
            raise ValueError("Cannot get visual value without both 'row_index' and 'value_column' in visual props.")
