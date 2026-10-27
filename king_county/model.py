"""Train, evaluate, save and load the notebook's final ElasticNet model.

The saved pipeline contains the feature pipeline too, so it predicts prices
directly from raw house records (the columns of the original CSV).

Run from the project root:
    uv run python -m king_county.model [--data PATH] [--output PATH] [--cv 5]
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import skops.io as sio
from sklearn.compose import TransformedTargetRegressor
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

from king_county.cleaning import RAW_DATA_PATH, drop_implausible_bedrooms, load_data
from king_county.pipeline import TARGET, make_feature_pipeline

MODEL_PATH = Path("model/model.bin")

# Same search space and split as the notebook.
PARAM_GRID = {
    "model__regressor__alpha": [0.01, 0.1, 1],
    "model__regressor__l1_ratio": [0.2, 0.5, 0.8],
}
TEST_SIZE = 0.3
RANDOM_STATE = 42


def make_model_pipeline() -> Pipeline:
    """Build the full pipeline: features, squared terms, scaling, ElasticNet.

    The target is standardized as well, so the regularization strength does
    not depend on prices being in the hundreds of thousands.
    """
    return Pipeline(
        [
            ("features", make_feature_pipeline()),
            ("polynomial", PolynomialFeatures(2, include_bias=False)),
            ("scaler", StandardScaler()),
            (
                "model",
                TransformedTargetRegressor(
                    regressor=ElasticNet(max_iter=5000, tol=1e-4, precompute=True),
                    transformer=StandardScaler(),
                ),
            ),
        ]
    )


def split_data(
    raw: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Drop implausible rows, then split raw records into train and test sets.

    Returns ``X_train, X_test, y_train, y_test`` like ``train_test_split``.
    The rows and their order match the notebook, so both use the same split.
    """
    raw = drop_implausible_bedrooms(raw)
    X = raw.drop(columns=[TARGET])
    y = raw[TARGET]
    return train_test_split(X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE)


def train_model(X_train: pd.DataFrame, y_train: pd.Series, cv: int = 5) -> GridSearchCV:
    """Tune and fit the model with cross-validated grid search.

    Every cleaning and feature step is refit inside each fold, so validation
    scores never see information from the rows they are scored on.
    """
    search = GridSearchCV(
        make_model_pipeline(), PARAM_GRID, cv=cv, scoring="r2", error_score="raise"
    )
    return search.fit(X_train, y_train)


def evaluate(model: Pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> dict[str, float]:
    """Return test-set R^2, mean absolute error and RMSE (both in dollars)."""
    predictions = model.predict(X_test)
    return {
        "r2": r2_score(y_test, predictions),
        "mae": mean_absolute_error(y_test, predictions),
        "rmse": root_mean_squared_error(y_test, predictions),
    }


def error_table(model: Pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> pd.DataFrame:
    """Return true and predicted prices per house, for the residual analysis."""
    predictions = model.predict(X_test)
    return pd.DataFrame(
        {
            "id": X_test["id"],
            "latitude": X_test["lat"],
            "longitude": X_test["long"],
            "price": y_test,
            "price_prediction": predictions.round(2),
            "price_difference": (predictions - y_test).round(2),
            "price_difference_percent": ((predictions - y_test) / y_test * 100).round(2),
        }
    ).reset_index(drop=True)


def save_model(model: Pipeline, path: str | Path = MODEL_PATH) -> Path:
    """Save a fitted pipeline with skops, creating the folder if needed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    sio.dump(model, path)
    return path


def load_model(path: str | Path = MODEL_PATH) -> Pipeline:
    """Load a pipeline saved by ``save_model``.

    skops refuses unknown types by default. Only types from this package and
    NumPy dtypes are accepted here; anything else in the file is an error.
    """
    untrusted = sio.get_untrusted_types(file=path)
    allowed = [t for t in untrusted if t.startswith(("king_county.", "numpy."))]
    unexpected = sorted(set(untrusted) - set(allowed))
    if unexpected:
        raise ValueError(f"Refusing to load unexpected types from {path}: {unexpected}")
    return sio.load(path, trusted=allowed)


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the King County price model.")
    parser.add_argument("--data", default=RAW_DATA_PATH, type=Path)
    parser.add_argument("--output", default=MODEL_PATH, type=Path)
    parser.add_argument("--cv", default=5, type=int)
    args = parser.parse_args()

    X_train, X_test, y_train, y_test = split_data(load_data(args.data))
    search = train_model(X_train, y_train, cv=args.cv)
    metrics = evaluate(search.best_estimator_, X_test, y_test)

    print(f"Train rows: {len(X_train)}, test rows: {len(X_test)}")
    print(f"Best parameters: {search.best_params_}")
    print(f"Mean cross-validation R^2: {search.best_score_:.3f}")
    print(
        f"Test R^2: {metrics['r2']:.3f}, MAE: ${metrics['mae']:,.0f}, "
        f"RMSE: ${metrics['rmse']:,.0f}"
    )
    coefficients = search.best_estimator_.named_steps["model"].regressor_.coef_
    print(f"Coefficients set to zero: {np.sum(coefficients == 0)} of {coefficients.size}")
    print(f"Saved model to {save_model(search.best_estimator_, args.output)}")


if __name__ == "__main__":
    main()
