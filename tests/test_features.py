import numpy as np
import pandas as pd
import pytest

from king_county.cleaning import clean_data, load_data
from king_county.features import (
    WEALTH_CENTER_LAT,
    WEALTH_CENTER_LONG,
    WaterDistance,
    add_center_distance,
    add_price_per_sqft,
    distance_km,
    nearest_distance_km,
)

KM_PER_DEGREE = 2 * np.pi * 6378 / 360


def test_distance_km_is_zero_for_the_same_point():
    assert distance_km(47.6, -122.3, 47.6, -122.3) == 0


def test_distance_km_for_one_degree_of_latitude():
    assert distance_km(48.6, -122.3, 47.6, -122.3) == pytest.approx(KM_PER_DEGREE)


def test_distance_km_shrinks_longitude_by_latitude():
    # At 60 degrees north, one degree of longitude is half a degree of latitude.
    assert distance_km(60, 1, 60, 0) == pytest.approx(KM_PER_DEGREE / 2)


def test_add_price_per_sqft_divides_by_living_plus_lot_area():
    df = pd.DataFrame({"price": [300000.0], "sqft_living": [1000], "sqft_lot": [2000]})
    assert add_price_per_sqft(df)["sqft_price"].iloc[0] == 100


def test_center_distance_is_zero_at_the_center():
    df = pd.DataFrame({"lat": [WEALTH_CENTER_LAT], "long": [WEALTH_CENTER_LONG]})
    assert add_center_distance(df)["center_distance"].iloc[0] == 0


def test_nearest_distance_picks_the_closest_reference():
    result = nearest_distance_km(
        lat=[47.0, 48.0], long=[-122.0, -122.0], ref_lat=[47.0, 49.0], ref_long=[-122.0, -122.0]
    )
    assert result == pytest.approx([0, KM_PER_DEGREE])


def test_water_distance_is_zero_for_waterfront_houses():
    df = pd.DataFrame(
        {"waterfront": [1, 0], "lat": [47.6, 47.7], "long": [-122.3, -122.3]}
    )
    result = WaterDistance().fit_transform(df)
    assert result["water_distance"].iloc[0] == 0
    assert result["water_distance"].iloc[1] == pytest.approx(0.1 * KM_PER_DEGREE)


def test_water_distance_measures_against_fitted_houses_only():
    train = pd.DataFrame({"waterfront": [1], "lat": [47.6], "long": [-122.3]})
    new = pd.DataFrame({"waterfront": [1], "lat": [47.7], "long": [-122.3]})
    result = WaterDistance().fit(train).transform(new)
    # The new house's own waterfront flag is ignored at transform time.
    assert result["water_distance"].iloc[0] == pytest.approx(0.1 * KM_PER_DEGREE)


def test_water_distance_needs_a_waterfront_house():
    df = pd.DataFrame({"waterfront": [0], "lat": [47.6], "long": [-122.3]})
    with pytest.raises(ValueError, match="waterfront"):
        WaterDistance().fit(df)


def notebook_water_distance(kc_data: pd.DataFrame) -> list[float]:
    """The notebook's original nested-loop implementation, kept as a reference."""

    def dist(long, lat, ref_long, ref_lat):
        delta_long = long - ref_long
        delta_lat = lat - ref_lat
        delta_long_corr = delta_long * np.cos(np.radians(ref_lat))
        return ((delta_long_corr) ** 2 + (delta_lat) ** 2) ** (1 / 2) * 2 * np.pi * 6378 / 360

    water_list = kc_data.query("waterfront == 1")
    water_distance = []
    for idx in kc_data.index:
        ref_list = []
        for x, y in zip(list(water_list["long"]), list(water_list["lat"])):
            ref_list.append(dist(kc_data["long"][idx], kc_data["lat"][idx], x, y).min())
        water_distance.append(min(ref_list))
    return water_distance


def test_water_distance_matches_the_notebook_loop_on_real_data():
    houses = clean_data(load_data()).sample(400, random_state=0)
    expected = notebook_water_distance(houses)
    result = WaterDistance().fit_transform(houses)["water_distance"]
    assert result.tolist() == pytest.approx(expected)
