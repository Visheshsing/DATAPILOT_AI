
import pandas as pd

from app.services.profiler import profile_dataset


def test_profile_dataset():

    df = pd.DataFrame({
        "sales": [100, 200, 300, 400],
        "profit": [10, 20, None, 40],
        "region": ["North", "South", "North", "West"]
    })

    schema, profile = profile_dataset(df)

    assert profile["shape"]["rows"] == 4
    assert profile["shape"]["columns"] == 3

    assert profile["missing_cells"] == 1

    assert profile["columns"]["sales"]["statistics"]["mean"] == 250

    assert schema["profit"]["null_count"] == 1


def test_duplicate_detection():

    df = pd.DataFrame({
        "sales": [100, 100, 200]
    })

    _, profile = profile_dataset(df)

    assert profile["duplicate_rows"] == 1
