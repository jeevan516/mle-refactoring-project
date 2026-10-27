"""Data cleaning steps from the "Data Preparation" section of the notebook.

Every function takes a DataFrame and returns a new one, so the steps can be
chained, tested in isolation, and reused inside a scikit-learn pipeline.
"""

from pathlib import Path

import pandas as pd

RAW_DATA_PATH = Path("data/King_County_House_prices_dataset.csv")

# The notebook found one listing with 33 bedrooms, 2 bathrooms and 1,620 sqft
# and dropped it as a data-entry error. Any count above this limit is treated
# the same way; the next-largest count in the data is 11.
MAX_BEDROOMS = 30


def load_data(path: str | Path = RAW_DATA_PATH) -> pd.DataFrame:
    """Read the raw King County house sales CSV."""
    return pd.read_csv(path)


def drop_implausible_bedrooms(
    df: pd.DataFrame, max_bedrooms: int = MAX_BEDROOMS
) -> pd.DataFrame:
    """Remove rows whose bedroom count is too large to be a real house.

    The notebook dropped the row by its index label (15856), which only works
    for this exact file. Filtering on the value works for any input.
    """
    return df[df["bedrooms"] <= max_bedrooms]


def recompute_basement(df: pd.DataFrame) -> pd.DataFrame:
    """Rebuild ``sqft_basement`` as ``sqft_living - sqft_above``.

    The raw column contains ``?`` entries, which make pandas read it as text.
    """
    return df.assign(sqft_basement=df["sqft_living"] - df["sqft_above"])


def fill_missing_flags(df: pd.DataFrame) -> pd.DataFrame:
    """Replace missing ``view`` and ``waterfront`` values with 0.

    0 is by far the most common value in both columns and fewer than 11% of
    rows are missing, so the most frequent value is a reasonable fill.
    """
    return df.fillna({"view": 0, "waterfront": 0})


def add_last_known_change(df: pd.DataFrame) -> pd.DataFrame:
    """Combine ``yr_built`` and ``yr_renovated`` into ``last_known_change``.

    The renovation year is used when there is one; a missing or 0 renovation
    year falls back to the build year. Both source columns are dropped.
    """
    renovated = df["yr_renovated"].fillna(0)
    last_known_change = renovated.where(renovated != 0, df["yr_built"]).astype(int)
    return df.assign(last_known_change=last_known_change).drop(
        columns=["yr_renovated", "yr_built"]
    )


def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Apply the column-level cleaning steps without removing any rows.

    This is the part of cleaning that also applies to new houses at
    prediction time, so it is safe to use inside a model pipeline.
    """
    return df.pipe(recompute_basement).pipe(fill_missing_flags).pipe(
        add_last_known_change
    )


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Run every cleaning step from the notebook, including row removal."""
    return df.pipe(drop_implausible_bedrooms).pipe(clean_columns)
