from __future__ import annotations

from typing import Any, Dict, Union, List
import pandas as pd

class RawDict(dict):
    """A dict whose keys are serialized verbatim (no snake_case → camelCase conversion).

    Use this when dict keys are data (e.g. column names) rather than property names,
    such as the ``fns`` mapping of a table ``totalRow``:

        total_row={"label": "Totals", "fns": RawDict({"unit_price": "avg"})}

    Values inside a RawDict are still serialized recursively.
    """


def snake_to_camel(key: str) -> str:
    """
    Converts a snake_case string to camelCase.

    Args:
        key (str): The snake_case string to convert.

    Returns:
        str: The converted camelCase string.
    """
    return "".join(word.capitalize() if i > 0 else word for i, word in enumerate(key.split("_")))


def camel_case_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively converts dictionary keys from snake_case to camelCase.

    Args:
        d (Dict[str, Any]): The dictionary to convert.

    Returns:
        Dict[str, Any]: A new dictionary with camelCase keys.
    """
    new_d: Dict[str, Any] = {}
    keep_keys = isinstance(d, RawDict)
    for k, v in d.items():
        camel_k = k if keep_keys else snake_to_camel(k)
        if isinstance(v, dict):
            new_d[camel_k] = camel_case_dict(v)
        elif isinstance(v, list):
            new_d[camel_k] = [camel_case_dict(i) if isinstance(i, dict) else i for i in v]
        else:
            new_d[camel_k] = v
    return new_d


def make_dataset_serializable(dataset: Dict[str, Any]) -> Dict[str, Any]:
    """
     prepares a dataset dictionary for serialization by removing internal objects.
    
    Specifically, it removes the '_df' key which stores the raw pandas DataFrame.

    Args:
        dataset (Dict[str, Any]): The dataset dictionary.

    Returns:
        Dict[str, Any]: A copy of the dataset dictionary ready for serialization.
    """
    serializable_dataset = dataset.copy()
    if "_df" in serializable_dataset:
        del serializable_dataset["_df"]
    return serializable_dataset


def convert_nan_to_none(value: Union[Dict,List,None,float,int,str]) -> Union[Dict,List,None,float,int,str]:
    """
    Recursively converts NaN values to None in a data structure.

    This is necessary for standard JSON serialization, which does not support NaN.

    Args:
        value (Union[Dict, List, None, float, int, str]): The value to process.

    Returns:
        Union[Dict, List, None, float, int, str]: The value with NaNs replaced by None.
    """
    if isinstance(value, dict):
        return {k: convert_nan_to_none(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [convert_nan_to_none(item) for item in value]
    elif isinstance(value, float) and pd.isna(value):  # Check for NaN
        return None
    else:
        return value