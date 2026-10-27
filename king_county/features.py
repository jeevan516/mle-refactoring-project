"""Feature engineering steps from the "Feature Engineering" section of the notebook."""

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

# Bill Gates' residence in Medina, used by the notebook as a "center of wealth".
WEALTH_CENTER_LAT = 47.62774
WEALTH_CENTER_LONG = -122.24194
# The notebook corrects longitude for the center distance at Seattle's latitude
# rather than at the center's own latitude. Kept as-is to reproduce its values.
CENTER_CORRECTION_LAT = 47.6219
# Radius used by the notebook; the equatorial radius of the Earth in km.
EARTH_RADIUS_KM = 6378


def distance_km(
    lat: np.ndarray | pd.Series,
    long: np.ndarray | pd.Series,
    ref_lat: np.ndarray | float,
    ref_long: np.ndarray | float,
    correction_lat: np.ndarray | float | None = None,
) -> np.ndarray:
    """Approximate distance in km between points and reference points.

    Uses the equirectangular approximation from the notebook: longitude
    differences are shrunk by ``cos(latitude)`` and the result is treated as a
    flat-plane distance. That is accurate to well under 1% over a county.
    Arguments broadcast like NumPy arrays, so one call can compare every house
    with every reference point.

    ``correction_lat`` is the latitude used for the longitude correction and
    defaults to ``ref_lat``.
    """
    if correction_lat is None:
        correction_lat = ref_lat
    delta_long = (np.asarray(long) - ref_long) * np.cos(np.radians(correction_lat))
    delta_lat = np.asarray(lat) - ref_lat
    return np.sqrt(delta_long**2 + delta_lat**2) * 2 * np.pi * EARTH_RADIUS_KM / 360


def add_price_per_sqft(df: pd.DataFrame) -> pd.DataFrame:
    """Add ``sqft_price``: sale price divided by living area plus lot area.

    The notebook describes this as price per square foot of living space but
    divides by ``sqft_living + sqft_lot``; the formula is kept as written.
    It is derived from the price, so it is for analysis only and must never be
    used as a model input.
    """
    return df.assign(sqft_price=(df["price"] / (df["sqft_living"] + df["sqft_lot"])).round(2))


def add_center_distance(df: pd.DataFrame) -> pd.DataFrame:
    """Add ``center_distance``: km from each house to the center of wealth."""
    center_distance = distance_km(
        df["lat"],
        df["long"],
        WEALTH_CENTER_LAT,
        WEALTH_CENTER_LONG,
        correction_lat=CENTER_CORRECTION_LAT,
    )
    return df.assign(center_distance=center_distance)


def nearest_distance_km(
    lat: np.ndarray | pd.Series,
    long: np.ndarray | pd.Series,
    ref_lat: np.ndarray,
    ref_long: np.ndarray,
) -> np.ndarray:
    """Return, for each point, the distance in km to its nearest reference point.

    Builds an (n_points, n_references) distance matrix in one vectorized call
    instead of the notebook's nested Python loop, which took several minutes.
    """
    lat = np.asarray(lat, dtype=float)[:, np.newaxis]
    long = np.asarray(long, dtype=float)[:, np.newaxis]
    distances = distance_km(lat, long, np.asarray(ref_lat), np.asarray(ref_long))
    return distances.min(axis=1)


class WaterDistance(TransformerMixin, BaseEstimator):
    """Add ``water_distance``: km to the nearest known waterfront house.

    Waterfront houses only roughly trace the shoreline, so this is a proxy for
    distance to the water. ``fit`` remembers the waterfront locations and
    ``transform`` measures against them. Inside a model pipeline that means
    the references come from the training rows only, so test rows do not leak
    their own waterfront flag into the feature.
    """

    def fit(self, X: pd.DataFrame, y: object = None) -> "WaterDistance":
        waterfront = X[X["waterfront"] == 1]
        if waterfront.empty:
            raise ValueError("Need at least one waterfront house to measure distances")
        self.ref_lat_ = waterfront["lat"].to_numpy(dtype=float)
        self.ref_long_ = waterfront["long"].to_numpy(dtype=float)
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        water_distance = nearest_distance_km(
            X["lat"], X["long"], self.ref_lat_, self.ref_long_
        )
        return X.assign(water_distance=water_distance)


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Run every feature engineering step from the notebook on cleaned data.

    The waterfront references come from ``df`` itself, as in the notebook.
    """
    return (
        df.pipe(add_price_per_sqft)
        .pipe(add_center_distance)
        .pipe(WaterDistance().fit_transform)
    )
