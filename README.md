# Refactoring Project

Use this repository as a **template** for your refactoring project. It walks you through turning a working but messy notebook into clean, reusable Python code: the notebook analyzes King County house sales, and your job is to extract its data cleaning and feature engineering logic into a proper pipeline. Create pull requests in your own copy even if you are working alone, and use them to track your progress.

## Learning Objectives

By the end of this repository, you should be able to:

- Read and understand an existing Data Science notebook well enough to refactor it.
- Refactor data cleaning and feature engineering code into reusable Python functions.
- Build a pipeline that reproduces a notebook's preprocessing steps end to end.
- Apply the same refactoring approach to a modeling workflow (stretch goal).
- Build and containerize a FastAPI CRUD service backed by a database (stretch goal).

## Learning Path

| File / Folder | Description |
|---|---|
| [**Project Description**](project-description.md) | The assignment tasks and stretch goals. |
| [**King County Notebook**](King-County.ipynb) | The original notebook: EDA, cleaning, feature engineering, and modeling for King County house prices. |
| [**Refactored Notebook**](King-County-refactored.ipynb) | The same workflow, calling the refactored `king_county` package. |
| [**Solution Notes**](SOLUTION.md) | What was built and the results compared with the notebook. The answers to the project questions are [below](#answers-to-the-project-questions). |

### Additional Folders and Files

| File / Folder | Description |
|---|---|
| [**data**](data/) | The King County house price dataset used by the notebook. |
| [**assets**](assets/) | Visual aids referenced in the repository. |
| [**bonus_solution**](bonus_solution/) | A FastAPI + Postgres + Docker reference implementation for the optional CRUD stretch goal. |
| [**king_county**](king_county/) | The refactored cleaning, feature engineering, pipeline, and modeling code. |
| [**tests**](tests/) | Tests for the `king_county` package. |
| [**api**](api/) | The FastAPI CRUD app for houses, with its Dockerfile and Compose file. |
| [**Dockerfile**](Dockerfile) | Images for training the model and running the tests. |
| [**docker-compose.yaml**](docker-compose.yaml) | Runs the API, database, training and tests together. |
| [**pyproject.toml**](pyproject.toml) | Project configuration and dependencies. |
| [**uv.lock**](uv.lock) | Dependency lock file. |

## Setup

Use [uv](https://docs.astral.sh/uv/getting-started/installation/) 0.13.5 or newer
and Python 3.13.17 or a newer 3.13 patch release, as defined in
[`.python-version`](.python-version).

Rebuild existing Docker images with `--pull --no-cache` after this update
to refresh their system certificates and dependencies.

> [!NOTE]
> Throughout these steps, text in angle brackets like `<repo-name>` is a **placeholder**. Replace it, including the `< >` brackets, with your own value. For example, `cd <repo-name>` becomes `cd mle-refactoring-project`.

### 1. Create the Repository from the Template

Click **Use this template** on GitHub.

When creating the repository:

- Set yourself as the **Owner**
- Choose a repository name
- Disable **Include all branches**
- Click **Create repository**

> [!IMPORTANT]
> If you are working in pairs or groups, only **one person** should complete this step.

---

### 2. Add Collaborators (Pairs/Groups Only)

If working with teammates:

1. Open the repository on GitHub
2. Go to **Settings → Collaborators**
3. Add your teammates as collaborators
4. Share the repository link with your team

Teammates should accept the invitation before continuing.

---

### 3. Clone the Repository

Copy the SSH URL from the **Code** button on GitHub, then run:

```bash
git clone <copied-ssh-url>
```

The copied SSH URL will look like `git@github.com:<your-username>/<repo-name>.git`.

---

### 4. Move into the Project Folder and Install Dependencies

This installs all dependencies and creates a virtual environment in `.venv/`.

```bash
cd <repo-name>
uv sync
```

---

### 5. Open the Repository in VS Code

> [!NOTE]
> Make sure you open VS Code from the project root so it automatically detects the environment created by `uv sync`.

Launch VS Code in the project root folder:

```bash
code .
```

Then open [King-County.ipynb](King-County.ipynb) and select the Python environment created by `uv sync` as the kernel.

## How to Use This Repo

1. Read the assignment brief in [project-description.md](project-description.md).
2. Work through the notebook in [King-County.ipynb](King-County.ipynb).
3. Refactor the cleaning and feature engineering logic into Python files.
4. Build a reusable pipeline.
5. If you want an extra challenge, extend your refactor to cover the modeling step as well.
6. If you want to go even further, use [bonus_solution/](bonus_solution/) as a reference for the optional FastAPI + Docker stretch goal.

## Using the Refactored Code

Run these commands from the project root.

Build the cleaned, feature-engineered dataset:

```python
from king_county.pipeline import prepare_data

kc_data = prepare_data()
```

Train the model, print its test scores, and save it to `model/model.bin`:

```bash
uv run python -m king_county.model
```

Load the saved model and predict prices from raw house records (the CSV's columns, without `price`):

```python
from king_county.model import load_model

model = load_model()
predictions = model.predict(raw_houses)
```

Run the tests:

```bash
uv run pytest
```

The API has its own setup; see [api/README.md](api/README.md).

## Run Everything With Docker

The root [docker-compose.yaml](docker-compose.yaml) runs the whole project in containers. It includes the API stack from [api/docker-compose.yaml](api/docker-compose.yaml) and adds two one-off jobs built from the root [Dockerfile](Dockerfile).

| Service | What it does | Command |
|---|---|---|
| `db`, `app` | Postgres and the houses API | `docker compose up -d --build --wait` |
| `train` | Trains the model, prints its scores, saves `model/model.bin` | `docker compose run --rm --build train` |
| `test` | Runs the `king_county` tests | `docker compose run --rm --build test` |

Before the first run, create the API settings:

```bash
cp api/.env.example api/.env
```

The API listens on the port set by `API_PORT` in `api/.env` (8000 by default). Stop the stack with `docker compose down`.

### Push the Images to a Registry

Images are tagged for a local registry at `localhost:5000` by default. Push all three with:

```bash
docker compose --profile train --profile test push
```

Set `REGISTRY` and `TAG` to push somewhere else, for example `REGISTRY=ghcr.io/<your-username> TAG=1.1`.

## Answers to the Project Questions

The answers below cover the tasks in [project-description.md](project-description.md). [SOLUTION.md](SOLUTION.md) summarizes what was built and compares the results with the original notebook.

### What steps did you take to complete the project?

1. **Read the notebook and ran it as a baseline.** I extracted its cleaning, feature engineering and modeling cells into a script and saved the resulting dataset and scores. Every later step was checked against this baseline.
2. **Separated what to keep from what to drop.** Exploration (`head`, `info`, `describe`, charts) stays in the notebook. Cleaning, feature engineering and modeling moved into the `king_county` package. Columns that were only used for one calculation (`delta_lat`, `delta_long`) are no longer created.
3. **Turned each notebook step into a small function.** Each cleaning and feature function takes a DataFrame and returns a new one, so the steps can be chained with `.pipe()` and tested on their own. None of them modifies its input.
4. **Built the pipeline in two forms.** `prepare_data()` rebuilds the notebook's analysis dataset in one call. `make_feature_pipeline()` wraps the same steps as a scikit-learn pipeline, so the trained model takes raw house records directly.
5. **Checked the refactor against the baseline.** The refactored dataset matches the notebook's values exactly, and the refactored model finds the same best parameters with the same test score (R² 0.845 against 0.844).
6. **Refactored the modeling step.** Splitting, grid search, evaluation, the residual table, and saving and loading are functions in `king_county/model.py`, with a command-line entry point.
7. **Made a refactored copy of the notebook** ([King-County-refactored.ipynb](King-County-refactored.ipynb)) that calls the package instead of repeating the code.
8. **Wrote tests** for each cleaning and feature step, the pipeline, the model and the API (37 in total), including one that compares the fast water-distance calculation with the notebook's original loop on real data.
9. **Built the FastAPI app** in its own `api/` folder with its own dependencies, so its image does not include pandas or scikit-learn.
10. **Added Docker support.** Docker Compose runs the API, Postgres, model training and the tests in containers, and pushes the images to a registry.

### What challenges did you face?

- **Steps that only worked for this exact file.** The 33-bedroom record was dropped by its row label (`drop(15856)`), which breaks for any other input. The refactor filters on the value instead (`bedrooms <= 30`).
- **A very slow feature.** The water distance used a nested Python loop over about 21,600 houses and 146 waterfront houses, which took around 400 seconds. Computing the whole distance matrix at once with NumPy takes about 0.1 seconds and gives the same values.
- **A small data leak.** In the notebook, every house, including test houses, measured its distance to *all* waterfront houses, so a waterfront house in the test set got a distance of 0 from its own label. Inside the model pipeline the waterfront locations now come from the training rows only, which is why the test R² differs slightly.
- **Code and text that disagree.** Reproducing the notebook exactly meant keeping some quirks, which are now documented in the code:
  - `sqft_price` is described as price per square foot of living space, but it divides by living area *plus* lot area.
  - The center distance corrects longitude at latitude 47.6219, not at the center's own latitude, 47.62774.
  - The modeling text talks about explaining "price per square foot", but the model's target is `price`.
  - The text says houses are "almost 19 km" from waterfront houses on average; the actual average is 5.5 km.
- **Library changes.** pandas 3.1 deprecates `inplace=True`, which the notebook uses, so the refactored functions return new DataFrames. skops will not load custom functions unless they are explicitly trusted, so `load_model` trusts only types from this package and refuses anything else.
- **Environment issues.** The project requires uv 0.13.5 or newer, so uv had to be upgraded, and terminals opened before the upgrade could not find `uv` until `PATH` was reloaded. Ports 8000 and 5432 were already used by other containers, so the API port is configurable and Postgres is not published on the host at all.

### What would you do differently if you had more time?

- **Treat `zipcode` as a category.** The model currently uses it as a number, and even squares it, which has no real meaning. One-hot encoding or target encoding would likely help.
- **Remove redundant features.** `sqft_basement` is exactly `sqft_living - sqft_above`, so one of the three columns adds nothing.
- **Try other targets and models.** Modeling the logarithm of the price would reduce the influence of very expensive houses, and tree-based models such as gradient boosting handle nonlinear effects without hand-made squared terms.
- **Use the sale date.** `date` is dropped entirely; month or season could explain part of the price.
- **Use real geography.** Shoreline data would describe distance to the water better than "distance to the nearest waterfront house", and the haversine formula would be more accurate over long distances.
- **Connect the API to the model.** The API stores five features, but the model needs nineteen. A prediction endpoint would need either more stored fields or a smaller model trained on the API's five features.
- **Production basics:** database migrations with Alembic instead of `create_all`, and a CI workflow that runs the tests and builds the images on every pull request.

## Bonus Solution

The [bonus_solution/](bonus_solution/) folder contains a minimal working example of:

- a FastAPI CRUD API
- Postgres persistence
- a `Dockerfile` for the API
- a `docker-compose.yaml` file to run the API and database together

It is included as a reference implementation for the optional stretch task, not as a required project structure.
