import numpy as np
import pytest

from king_county.cleaning import load_data
from king_county.model import (
    error_table,
    evaluate,
    load_model,
    make_model_pipeline,
    save_model,
    split_data,
    train_model,
)


@pytest.fixture(scope="module")
def split():
    # A sample keeps the grid search fast while still covering every step.
    return split_data(load_data().sample(3000, random_state=0))


def test_split_data_holds_out_30_percent(split):
    X_train, X_test, y_train, y_test = split
    assert len(X_test) == pytest.approx(0.3 * (len(X_train) + len(X_test)), abs=1)
    assert "price" not in X_train
    assert len(X_train) == len(y_train)


def test_trained_model_beats_predicting_the_mean(split):
    X_train, X_test, y_train, y_test = split
    model = train_model(X_train, y_train, cv=2).best_estimator_
    metrics = evaluate(model, X_test, y_test)
    assert metrics["r2"] > 0.5
    assert metrics["mae"] > 0


def test_error_table_has_one_row_per_test_house(split):
    X_train, X_test, y_train, y_test = split
    model = make_model_pipeline().fit(X_train, y_train)
    table = error_table(model, X_test, y_test)
    assert len(table) == len(X_test)
    assert (table["price_prediction"] - table["price"]).round(2).equals(
        table["price_difference"]
    )


def test_saved_model_predicts_the_same_after_loading(split, tmp_path):
    X_train, X_test, y_train, _ = split
    model = make_model_pipeline().fit(X_train, y_train)
    path = save_model(model, tmp_path / "model.bin")
    np.testing.assert_allclose(load_model(path).predict(X_test), model.predict(X_test))
