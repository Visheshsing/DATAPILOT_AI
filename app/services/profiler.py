
import pandas as pd
import numpy as np


def clean_value(value):

    if pd.isna(value):
        return None

    if isinstance(value, (np.integer,)):
        return int(value)

    if isinstance(value, (np.floating,)):
        return float(value)

    if isinstance(value, (np.bool_,)):
        return bool(value)

    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()

    return str(value) if not isinstance(
        value, (str, int, float, bool)
    ) else value


def profile_dataset(df: pd.DataFrame):

    schema = {}
    column_profiles = {}

    for column in df.columns:

        series = df[column]

        schema[column] = {
            "dtype": str(series.dtype),
            "null_count": int(series.isna().sum()),
            "unique_count": int(series.nunique()),
        }

        details = {
            "missing_percentage": round(
                float(series.isna().mean() * 100), 2
            ),
            "unique_count": int(series.nunique()),
        }

        if pd.api.types.is_numeric_dtype(series):

            numeric = series.dropna()

            details["statistics"] = {
                "mean": clean_value(numeric.mean()),
                "median": clean_value(numeric.median()),
                "std": clean_value(numeric.std()),
                "min": clean_value(numeric.min()),
                "max": clean_value(numeric.max()),
                "q25": clean_value(numeric.quantile(0.25)),
                "q75": clean_value(numeric.quantile(0.75)),
            }

        else:

            top_values = series.value_counts(
                dropna=True
            ).head(5)

            details["top_values"] = {
                str(key): int(value)
                for key, value in top_values.items()
            }

        column_profiles[column] = details

    profile = {
        "shape": {
            "rows": int(df.shape[0]),
            "columns": int(df.shape[1]),
        },
        "duplicate_rows": int(df.duplicated().sum()),
        "missing_cells": int(df.isna().sum().sum()),
        "memory_usage_bytes": int(
            df.memory_usage(deep=True).sum()
        ),
        "columns": column_profiles,
    }

    return schema, profile
