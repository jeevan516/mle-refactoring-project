"""Reusable data cleaning and feature engineering pipeline.

Two entry points cover the two ways the notebook uses its data:

- ``prepare_data`` reproduces the notebook's fully cleaned and engineered
  DataFrame for exploration and analysis.
- ``make_feature_pipeline`` wraps the same steps as a scikit-learn pipeline
  that turns raw house records into model features, for training and for
  predicting the price of new houses.
"""

from pathlib import Path

import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer

from king_county.cleaning import RAW_DATA_PATH, clean_columns, clean_data, load_data
from king_county.features import WaterDistance, add_center_distance, engineer_features

TARGET = "price"

# Model inputs, in the order the notebook passed them to the model. Excluded:
# `id` (an identifier), `date` (not used by the notebook), and `price` and
# `sqft_price` (the target and a value derived from it, which would leak).
FEATURES = [
    "bedrooms",
    "bathrooms",
    "sqft_living",
    "sqft_lot",
    "floors",
    "waterfront",
    "view",
    "condition",
    "grade",
    "sqft_above",
    "sqft_basement",
    "zipcode",
    "lat",
    "long",
    "sqft_living15",
    "sqft_lot15",
    "last_known_change",
    "center_distance",
    "water_distance",
]


def prepare_data(path: str | Path = RAW_DATA_PATH) -> pd.DataFrame:
    """Load the raw CSV and return the notebook's cleaned, engineered data."""
    return load_data(path).pipe(clean_data).pipe(engineer_features)


def select_features(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only the model input columns, in a fixed order."""
    return df[FEATURES]


def make_feature_pipeline() -> Pipeline:
    """Build a pipeline that turns raw house records into model features.

    The input has the raw CSV columns (``price`` is not needed). No rows are
    removed, so it can score any house; drop implausible training rows with
    ``clean_data`` or ``drop_implausible_bedrooms`` before fitting.
    """
    return Pipeline(
        [
            ("clean", FunctionTransformer(clean_columns)),
            ("center_distance", FunctionTransformer(add_center_distance)),
            ("water_distance", WaterDistance()),
            ("select", FunctionTransformer(select_features)),
        ]
    )
