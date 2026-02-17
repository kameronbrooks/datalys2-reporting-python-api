from __future__ import annotations

from typing import Any, Dict, List, Optional

import pandas as pd

from ..serialization import camel_case_dict, snake_to_camel
from ..utilities import analytics
from .base import ReportTreeComponent

_TREND_ALLOWED_TYPES = frozenset({"line", "scatter", "clusteredBar", "stackedBar"})


class Visual(ReportTreeComponent):
    """
    Represents a visualization component in the report.
    """
    def __init__(self, type: str, dataset_id: Optional[str] = None, **kwargs):
        """
        Initializes a new Visual.

        Args:
            type (str): The type of visual (e.g., 'bar', 'line', 'scatter').
            dataset_id (str, optional): The ID of the dataset this visual will use. Defaults to None.
            **kwargs: Additional properties for the visual (e.g., x_column, y_column).
        """
        super().__init__()
        self.type = type
        self.dataset_id = dataset_id
        self.other_elements: List[Dict[str, Any]] = []
        self.props = kwargs

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

        This method is only supported for 'line', 'scatter', 'clusteredBar', and 'stackedBar' visuals.
        If coefficients are not provided, it attempts to auto-calculate them using the visual's dataset
        and properties (specifically x_column and y_column).

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
                "Trend elements can only be added to line, scatter, clusteredBar, or stackedBar visuals."
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
