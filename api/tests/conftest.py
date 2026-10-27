import os
import tempfile
from pathlib import Path

import pytest

# app.database reads DB_CONN at import time, so point it at a throwaway
# SQLite file before the app is imported. No Postgres server is needed.
_db_file = Path(tempfile.mkdtemp()) / "test.db"
os.environ["DB_CONN"] = f"sqlite:///{_db_file.as_posix()}"

from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
def client():
    """A test client with an empty houses table for every test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
