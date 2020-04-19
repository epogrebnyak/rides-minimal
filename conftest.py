import pytest

from search import yield_trips


def get_dataframe():
    import pandas as pd

    df = pd.read_csv("one_day.zip", parse_dates=["time"])
    assert df.shape == (131842, 6)
    return df


@pytest.fixture
def trips():
    return list(yield_trips(get_dataframe()))
