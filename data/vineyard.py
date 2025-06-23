import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, Date, Numeric
from sqlmodel import Field, Relationship, SQLModel


class Vineyard(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    address: Optional[str] = Field(default=None)

    management_units: list["ManagementUnit"] = Relationship(back_populates="vineyard")


class Variety(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)  # e.g. "Cabernet Sauvignon"
    wine_colour_id: int = Field(foreign_key="winecolour.id")

    wine_colour: "WineColour" = Relationship(back_populates="varieties")
    management_units: list["ManagementUnit"] = Relationship(back_populates="variety")


class Status(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    status: str = Field(default="Active")

    management_units: list["ManagementUnit"] = Relationship(back_populates="status")


class ManagementUnit(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    variety_name_modifier: Optional[str] = Field(default=None)

    area: Decimal = Field(sa_column=Column(Numeric(5, 2)))
    row_width: Decimal = Field(sa_column=Column(Numeric(3, 2)))
    vine_spacing: Decimal = Field(sa_column=Column(Numeric(3, 2)))

    rows_total: Optional[int] = Field(default=None)
    rows_start_number: Optional[int] = Field(default=None)
    rows_end_number: Optional[int] = Field(default=None)
    date_planted: datetime.datetime | None = Field(sa_column=Column(Date))

    variety_id: int | None = Field(default=None, foreign_key="variety.id")
    vineyard_id: int | None = Field(default=None, foreign_key="vineyard.id")
    status_id: int | None = Field(default=None, foreign_key="status.id")

    variety: Variety | None = Relationship(back_populates="management_units")
    vineyard: Vineyard | None = Relationship(back_populates="management_units")
    status: Status | None = Relationship(back_populates="management_units")


class WineColour(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)  # e.g. "Red", "White"

    varieties: list["Variety"] = Relationship(back_populates="wine_colour")
