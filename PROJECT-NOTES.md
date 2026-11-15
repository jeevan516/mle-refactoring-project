# King County refactoring: project notes

_Last updated: 15 Nov 2026_

## Project
**From notebook to pipeline.** A working but messy notebook predicts King County house prices.
The goal is to move its cleaning, features and model into reusable, tested Python, and to add
an API and Docker as stretch goals.

- **Data:** King County house sales (`data/King_County_House_prices_dataset.csv`),
  21,597 raw rows, 21,596 after cleaning, 21 columns.
- **Model:** scikit-learn pipeline with 19 features → ElasticNet, tuned with grid search;
  saved with `skops`.
- **Stack:** `king_county` package (`cleaning.py`, `features.py`, `pipeline.py`, `model.py`),
  FastAPI + Postgres CRUD app in `api/`, Docker Compose, GitHub Actions.

## Approach
1. **Baseline:** ran the original notebook and saved its dataset and scores to compare against.
2. **Keep or move:** exploration stays in the notebook; cleaning, features and modeling move out.
3. **Small functions:** each step takes a DataFrame and returns a new one, chained with `.pipe()`.
4. **Pipeline in two forms:** `prepare_data()` rebuilds the dataset; `make_feature_pipeline()`
   lets the trained model take raw house records.
5. **Check against the baseline:** same dataset, same best parameters, nearly the same R².
6. **Modeling:** split, grid search, evaluation, save and load, plus a command-line entry point;
   a refactored copy of the notebook calls the package.
7. **Tests:** every cleaning and feature step, the pipeline, the model and the API.
8. **API and Docker:** FastAPI CRUD app with 5 house features; Compose runs the API, Postgres,
   training and tests; Portainer stack file; Docker Image CI workflow.
9. **Presentation:** full deck and a 5-slide version in `presentation/`.

## Results
| Check | Result |
|---|---|
| Cleaned dataset | **21,596 rows**, identical to the notebook, checked column by column |
| `water_distance` feature | about **400 s → 0.1 s** (NumPy distance matrix instead of a nested loop) |
| Best ElasticNet parameters | `alpha=0.01`, `l1_ratio=0.2`, same as the notebook |
| Mean cross-validation R² | **0.828** |
| Test R² | **0.845** (original notebook 0.844; small gap from fixing a data leak) |
| Test MAE / RMSE | **$94,808** / **$143,443** |
| Tests | **37 / 37 pass**: 24 package + 13 API (re-run 15 Nov 2026) |
| CI (`docker-image.yml`) | builds the test and training images, runs tests in Docker, starts the API and checks `/` and `/houses` |

Sources: refactored notebook outputs (cells 3, 7, 8), `SOLUTION.md`, `README.md`,
`pptx/decks.py` (`mle_refactoring`), pytest runs.

## Future engineering
- Treat `zipcode` as a category; today it is used as a number and even squared.
- Predict log(price) to reduce the pull of very expensive houses.
- Try gradient boosting for nonlinear effects without hand-made squared terms.
- Use the sale date (month or season); drop the redundant `sqft_basement`.
- Add a `/predict` endpoint; the API stores 5 features but the model needs 19.
- Alembic migrations instead of `create_all`; run the pytest suite in CI on every pull request.

## Update log
- 27 Oct 2026: notebook refactored into a pipeline with API, Docker and tests; Portainer
  stack, Dockerfile and Docker Image CI added; PR #1 merged.
- 10 Nov 2026: project presentation added, plus a 5-slide version.
- 15 Nov 2026: project notes created.
