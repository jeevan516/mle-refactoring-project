"""Database table for stored houses."""

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class House(Base):
    """One house, described by five of the dataset's columns."""

    __tablename__ = "houses"

    id: Mapped[int] = mapped_column(primary_key=True)
    bedrooms: Mapped[int] = mapped_column(Integer)
    bathrooms: Mapped[float] = mapped_column(Float)
    sqft_living: Mapped[int] = mapped_column(Integer)
    grade: Mapped[int] = mapped_column(Integer)
    # Stored as text so leading zeros would survive; King County codes are 98xxx.
    zipcode: Mapped[str] = mapped_column(String(5), index=True)
