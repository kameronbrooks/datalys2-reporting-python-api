from __future__ import annotations

from typing import Any, Dict, Union, List
import pandas as pd

def snake_to_camel(key: str) -> str:
    return "".join(word.capitalize() if i > 0 else word for i, word in enumerate(key.split("_")))


def camel_case_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    new_d: Dict[str, Any] = {}
    for k, v in d.items():
        camel_k = snake_to_camel(k)
        if isinstance(v, dict):
            new_d[camel_k] = camel_case_dict(v)
        elif isinstance(v, list):
            new_d[camel_k] = [camel_case_dict(i) if isinstance(i, dict) else i for i in v]
        else:
            new_d[camel_k] = v
    return new_d


def make_dataset_serializable(dataset: Dict[str, Any]) -> Dict[str, Any]:
    serializable_dataset = dataset.copy()
    if "_df" in serializable_dataset:
        del serializable_dataset["_df"]
    return serializable_dataset


def convert_nan_to_none(value: Union[Dict,List,None,float,int,str]) -> Union[Dict,List,None,float,int,str]:
    if isinstance(value, dict):
        return {k: convert_nan_to_none(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [convert_nan_to_none(item) for item in value]
    elif isinstance(value, float) and pd.isna(value):  # Check for NaN
        return None
    else:
        return value