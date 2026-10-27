# Solution Notes

This file lists what was built for the [project description](project-description.md) and compares the results with the original notebook. The answers to the project questions are in the [README](README.md#answers-to-the-project-questions).

## What Was Built

| Task | Where | Status |
|---|---|---|
| Refactor cleaning and feature engineering into Python files | [king_county/cleaning.py](king_county/cleaning.py), [king_county/features.py](king_county/features.py) | Done |
| Reusable pipeline | [king_county/pipeline.py](king_county/pipeline.py) | Done |
| Refactor the modeling step (stretch) | [king_county/model.py](king_county/model.py) | Done |
| Refactored copy of the notebook | [King-County-refactored.ipynb](King-County-refactored.ipynb) | Done |
| FastAPI CRUD app with 5 features (stretch) | [api/](api/) | Done |
| Dockerfile and Compose file, running in a container (stretch) | [api/Dockerfile](api/Dockerfile), [api/docker-compose.yaml](api/docker-compose.yaml) | Done |
| Root Docker Compose for the API, training and tests; images pushed to a registry | [Dockerfile](Dockerfile), [docker-compose.yaml](docker-compose.yaml) | Done |
| Tests (extra) | [tests/](tests/) (24 tests), [api/tests/](api/tests/) (13 tests) | Done |

### Results Compared With the Notebook

| | Original notebook | Refactored |
|---|---|---|
| Cleaned and engineered dataset | 21,596 rows | Identical values, checked column by column |
| Time to compute `water_distance` | about 400 seconds | about 0.1 seconds |
| Best ElasticNet parameters | `alpha=0.01`, `l1_ratio=0.2` | Same |
| Test R² | 0.844 | 0.845 |
