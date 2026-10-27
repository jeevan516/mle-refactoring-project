import pandas as pd

from king_county.cleaning import (
    add_last_known_change,
    clean_columns,
    clean_data,
    drop_implausible_bedrooms,
    fill_missing_flags,
    recompute_basement,
)


def test_drop_implausible_bedrooms_removes_only_the_outlier(raw_houses):
    result = drop_implausible_bedrooms(raw_houses)
    assert result["id"].tolist() == [1, 3, 4, 5]


def test_recompute_basement_replaces_question_marks(raw_houses):
    result = recompute_basement(raw_houses)
    assert result["sqft_basement"].tolist() == [0, 580, 0, 910, 0]
    assert pd.api.types.is_integer_dtype(result["sqft_basement"])


def test_fill_missing_flags_uses_zero(raw_houses):
    result = fill_missing_flags(raw_houses)
    assert result["waterfront"].tolist() == [0, 0, 0, 1, 0]
    assert result["view"].tolist() == [0, 0, 0, 3, 0]
    # Other columns keep their missing values.
    assert result["yr_renovated"].isna().sum() == 2


def test_add_last_known_change_prefers_renovation_year(raw_houses):
    result = add_last_known_change(raw_houses)
    # Renovated only in row 3; 0 and missing fall back to the build year.
    assert result["last_known_change"].tolist() == [1955, 1947, 2002, 1965, 1987]
    assert "yr_built" not in result
    assert "yr_renovated" not in result


def test_cleaning_does_not_modify_its_input(raw_houses):
    original = raw_houses.copy()
    clean_data(raw_houses)
    pd.testing.assert_frame_equal(raw_houses, original)


def test_clean_columns_keeps_every_row(raw_houses):
    assert len(clean_columns(raw_houses)) == len(raw_houses)


def test_clean_data_leaves_no_missing_values(raw_houses):
    result = clean_data(raw_houses)
    assert len(result) == 4
    assert not result.isna().any().any()
