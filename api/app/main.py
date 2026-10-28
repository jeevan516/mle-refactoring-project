"""FastAPI app with create, read, update and delete endpoints for houses."""

from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import Base, engine, get_db

app = FastAPI(
    title="King County Houses API",
    description="Store and manage King County houses described by five features.",
    version="1.0.0",
)

# Create missing tables at startup. Not a migration tool: an existing table
# is left unchanged if the model changes.
Base.metadata.create_all(bind=engine)

DatabaseSession = Annotated[Session, Depends(get_db)]

# The browser page is one static file that calls the endpoints below.
INDEX_HTML = (Path(__file__).parent / "static" / "index.html").read_text(encoding="utf-8")


def get_house_or_404(db: Session, house_id: int) -> models.House:
    """Return one house or raise the public not-found response."""
    house = db.get(models.House, house_id)
    if house is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"House {house_id} was not found.",
        )
    return house


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def index() -> str:
    """Serve the browser page for managing houses."""
    return INDEX_HTML


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    """Return a lightweight service status response."""
    return {"status": "ok"}


@app.get("/houses", response_model=list[schemas.HouseOut], tags=["houses"])
def get_all_houses(
    db: DatabaseSession,
    zipcode: Annotated[str | None, Query(pattern=r"^\d{5}$")] = None,
) -> list[models.House]:
    """Return stored houses ordered by id, optionally only one zip code."""
    statement = select(models.House).order_by(models.House.id)
    if zipcode is not None:
        statement = statement.where(models.House.zipcode == zipcode)
    return list(db.scalars(statement))


@app.get("/houses/{house_id}", response_model=schemas.HouseOut, tags=["houses"])
def get_house(house_id: int, db: DatabaseSession) -> models.House:
    """Return one stored house."""
    return get_house_or_404(db, house_id)


@app.post(
    "/houses",
    response_model=schemas.HouseOut,
    status_code=status.HTTP_201_CREATED,
    tags=["houses"],
)
def create_house(request: schemas.HouseCreate, db: DatabaseSession) -> models.House:
    """Validate and store a new house."""
    new_house = models.House(**request.model_dump())
    db.add(new_house)
    db.commit()
    # Reload the row to pick up the database-generated id.
    db.refresh(new_house)
    return new_house


@app.put("/houses/{house_id}", response_model=schemas.HouseOut, tags=["houses"])
def update_house(
    house_id: int, request: schemas.HouseUpdate, db: DatabaseSession
) -> models.House:
    """Replace every editable field of one house."""
    house = get_house_or_404(db, house_id)
    for field, value in request.model_dump().items():
        setattr(house, field, value)
    db.commit()
    db.refresh(house)
    return house


@app.delete(
    "/houses/{house_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["houses"]
)
def delete_house(house_id: int, db: DatabaseSession) -> Response:
    """Delete one house or return 404 when it does not exist."""
    house = get_house_or_404(db, house_id)
    db.delete(house)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
