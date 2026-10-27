"""Request and response bodies for the houses API."""

from pydantic import BaseModel, ConfigDict, Field


class HouseBase(BaseModel):
    """Fields shared by create, update and response bodies.

    The limits follow the cleaned dataset: bedrooms run from 0 to 11 after
    the 33-bedroom error is removed, bathrooms come in quarter steps, and
    grade is King County's 1-13 construction quality scale.
    """

    bedrooms: int = Field(ge=0, le=30, examples=[3])
    bathrooms: float = Field(ge=0, le=10, multiple_of=0.25, examples=[2.5])
    sqft_living: int = Field(gt=0, le=20000, examples=[1800])
    grade: int = Field(ge=1, le=13, examples=[8])
    zipcode: str = Field(pattern=r"^\d{5}$", examples=["98103"])


class HouseCreate(HouseBase):
    """Request body used to create a house."""


class HouseUpdate(HouseBase):
    """Request body used to replace every field of a house."""


class HouseOut(HouseBase):
    """Response body returned for stored houses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
