from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, Numeric
from sqlmodel import Field, Relationship, SQLModel


class Vineyard(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    address: str

    management_units: list["ManagementUnit"] = Relationship(back_populates="vineyard")


class Variety(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)  # e.g. "Cabernet Sauvignon"
    clone_name: Optional[str] = Field(default=None)
    wine_colour_id: int = Field(foreign_key="winecolour.id")

    wine_colour: "WineColour" = Relationship(back_populates="varieties")
    management_units: list["ManagementUnit"] = Relationship(back_populates="variety")


class ManagementUnit(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    area: Decimal = Field(sa_column=Column(Numeric(5, 2)))
    row_width: Decimal = Field(sa_column=Column(Numeric(3, 2)))
    vine_spacing: Decimal = Field(sa_column=Column(Numeric(3, 2)))

    rows_total: Optional[int] = Field(default=None)
    rows_start_number: Optional[int] = Field(default=None)
    rows_end_number: Optional[int] = Field(default=None)

    variety_id: int | None = Field(default=None, foreign_key="variety.id")
    vineyard_id: int | None = Field(default=None, foreign_key="vineyard.id")

    variety: Variety | None = Relationship(back_populates="management_units")
    vineyard: Vineyard | None = Relationship(back_populates="management_units")


"""     @model_validator(mode="wrap")
    @classmethod
    def check_row_consistency(cls, values):
        start, end, total = (
            values.get("rows_start_number"),
            values.get("rows_end_number"),
            values.get("rows_total"),
        )
        if start and end and start > end:
            raise ValueError(
                "Start row number must be less than or equal to end row number"
            )
        if start and end and total and total != (end - start + 1):
            raise ValueError("rows_total does not match start and end range")
        return values """


class WineColour(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)  # e.g. "Red", "White"

    varieties: list["Variety"] = Relationship(back_populates="wine_colour")
