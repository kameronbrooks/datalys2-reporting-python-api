from __future__ import annotations

from typing import Any, Dict, List, Optional

import pandas as pd

from ..serialization import camel_case_dict, snake_to_camel
from ..utilities import analytics
from .base import ReportTreeComponent


class Visual(ReportTreeComponent):
    def __init__(self, type: str, dataset_id: Optional[str] = None, **kwargs):
        super().__init__()
        self.type = type
        self.dataset_id = dataset_id
        self.other_elements: List[Dict[str, Any]] = []
        self.props = kwargs

    def add_element(self, type: str, **kwargs) -> Visual:
        """Adds a visual element (annotation) to the visual."""

        element = {"visual_element_type": type}
        element.update(kwargs)
        self.other_elements.append(element)
        return self

    def add_trend(self, coefficients: (List[float] | int | None) = None, **kwargs) -> Visual:
        """Adds a trend line element to the visual."""

        # TODO: Only allow trends for certain visual types?
        if self.type not in ["line", "scatter", "bar"]:
            raise ValueError("Trend elements can only be added to line, scatter, or bar visuals.")

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
        d: Dict[str, Any] = {
            "type": self.type,
            "elementType": "visual",
        }
        if self.dataset_id:
            d["datasetId"] = self.dataset_id

        if self.other_elements:
            d["otherElements"] = [camel_case_dict(e) for e in self.other_elements]

        for k, v in self.props.items():
            camel_k = snake_to_camel(k)
            if isinstance(v, dict):
                d[camel_k] = camel_case_dict(v)
            elif isinstance(v, list):
                d[camel_k] = [camel_case_dict(i) if isinstance(i, dict) else i for i in v]
            else:
                d[camel_k] = v
        return d
