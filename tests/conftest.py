import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def raw_houses() -> pd.DataFrame:
    """Five raw records with the CSV's columns and its known data problems."""
    return pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "date": ["10/13/2014", "12/9/2014", "2/25/2015", "12/9/2014", "2/18/2015"],
            "price": [221900.0, 538000.0, 180000.0, 604000.0, 510000.0],
            "bedrooms": [3, 33, 2, 4, 3],
            "bathrooms": [1.0, 2.0, 1.0, 3.0, 2.0],
            "sqft_living": [1180, 1620, 770, 1960, 1680],
            "sqft_lot": [5650, 6000, 10000, 5000, 8080],
            "floors": [1.0, 1.0, 1.0, 1.0, 1.0],
            "waterfront": [np.nan, 0.0, 0.0, 1.0, 0.0],
            "view": [0.0, np.nan, 0.0, 3.0, 0.0],
            "condition": [3, 5, 3, 5, 3],
            "grade": [7, 7, 6, 7, 8],
            "sqft_above": [1180, 1040, 770, 1050, 1680],
            "sqft_basement": ["0.0", "580.0", "?", "910.0", "0.0"],
            "yr_built": [1955, 1947, 1933, 1965, 1987],
            "yr_renovated": [0.0, np.nan, 2002.0, 0.0, np.nan],
            "zipcode": [98178, 98103, 98028, 98136, 98074],
            "lat": [47.5112, 47.6878, 47.7379, 47.5208, 47.6168],
            "long": [-122.257, -122.331, -122.233, -122.393, -122.045],
            "sqft_living15": [1340, 1330, 2720, 1360, 1800],
            "sqft_lot15": [5650, 4700, 8062, 5000, 7503],
        }
    )
