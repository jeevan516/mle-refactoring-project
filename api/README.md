# King County Houses API

A FastAPI service that stores houses in Postgres and supports create, read, update and delete. Each house has five features, named after the matching columns in the King County dataset:

| Field | Type | Allowed values |
|---|---|---|
| `bedrooms` | integer | 0 to 30 |
| `bathrooms` | number | 0 to 10, in steps of 0.25 |
| `sqft_living` | integer | 1 to 20,000 |
| `grade` | integer | 1 to 13 (King County construction grade) |
| `zipcode` | text | exactly 5 digits, for example `"98103"` |

Invalid values are rejected with status `422` before anything reaches the database.

## Endpoints

| Method and path | Purpose | Success status |
|---|---|---|
| `GET /` | Web page to list, filter, add, edit and delete houses | 200 |
| `GET /health` | Health check | 200 |
| `POST /houses` | Create a house | 201 |
| `GET /houses` | List houses by id; optional `?zipcode=98103` filter | 200 |
| `GET /houses/{house_id}` | Read one house | 200 |
| `PUT /houses/{house_id}` | Replace all five fields of a house | 200 |
| `DELETE /houses/{house_id}` | Delete a house | 204 |

Reading, updating or deleting a house that does not exist returns `404`.

## Run With Docker Compose

From this `api/` folder:

```bash
cp .env.example .env
docker compose up --build --wait
```

Open <http://localhost:8000> to manage houses in the browser, or <http://localhost:8000/docs> to try the endpoints directly. If port 8000 is already in use, set `API_PORT` in `.env` (for example `API_PORT=8001`) and use that port instead.

Postgres is not published on a host port; only the API connects to it, over the Compose network. Its data is kept in the `king-county-api_postgres-data` volume between runs.

Stop the stack with `docker compose down`. Add `--volumes` only when you also want to delete the stored houses.

## Example Request

```bash
curl -X POST http://localhost:8000/houses \
  -H "Content-Type: application/json" \
  -d '{"bedrooms": 3, "bathrooms": 2.5, "sqft_living": 1800, "grade": 8, "zipcode": "98103"}'
```

## Tests

The tests use a temporary SQLite file instead of Postgres, so no database server is needed:

```bash
uv run pytest
```

## Files

| File | Purpose |
|---|---|
| `app/database.py` | Reads `DB_CONN`, creates the engine and one session per request |
| `app/models.py` | The `houses` table |
| `app/schemas.py` | Request and response bodies, including the validation limits |
| `app/main.py` | The endpoints |
| `app/static/index.html` | The browser page served at `/`; plain HTML, CSS and JavaScript calling the endpoints |
| `Dockerfile` | Image for the API, running as a non-root user |
| `docker-compose.yaml` | Starts Postgres and the API, with health checks |
