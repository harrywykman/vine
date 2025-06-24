import datetime
from decimal import Decimal
from typing import Optional

import sqlalchemy as sa
from sqlmodel import Field, Relationship, SQLModel

###### CORE VINEYARD MODELS ########


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

    area: Decimal = Field(sa_column=sa.Column(sa.Numeric(5, 2)))
    row_width: Decimal = Field(sa_column=sa.Column(sa.Numeric(3, 2)))
    vine_spacing: Decimal = Field(sa_column=sa.Column(sa.Numeric(3, 2)))

    rows_total: Optional[int] = Field(default=None)
    rows_start_number: Optional[int] = Field(default=None)
    rows_end_number: Optional[int] = Field(default=None)
    date_planted: datetime.datetime | None = Field(sa_column=sa.Column(sa.Date))

    spray_records: list["SprayRecord"] = Relationship(back_populates="management_unit")

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


###### SPRAY RELATED MODELS ########


class SprayProgram(SQLModel, table=True):
    __tablename__ = "spray_programs"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    water_spray_rate_per_hectare: Decimal = Field(
        default=0, max_digits=5, decimal_places=2, nullable=False
    )
    date_created: datetime.datetime = Field(
        sa_column=sa.Column(sa.DateTime, default=datetime.datetime.now, index=True)
    )

    spray_program_chemicals: list["SprayProgramChemical"] = Relationship(
        back_populates="spray_program"
    )
    spray_records: list["SprayRecord"] = Relationship(back_populates="spray_program")


class SprayRecord(SQLModel, table=True):
    __tablename__ = "spray_records"

    id: Optional[int] = Field(default=None, primary_key=True)
    operator: str
    complete: bool
    date_created: datetime.datetime = Field(
        sa_column=sa.Column(sa.DateTime, default=datetime.datetime.now, index=True)
    )
    # TODO: Add Growth Stage

    management_unit_id: int = Field(foreign_key="managementunit.id", nullable=False)
    spray_program_id: int = Field(foreign_key="spray_programs.id", nullable=False)

    management_unit: ManagementUnit = Relationship(back_populates="spray_records")
    spray_program: SprayProgram = Relationship(back_populates="spray_records")


class SprayProgramChemical(SQLModel, table=True):
    __tablename__ = "spray_program_chemicals"

    id: Optional[int] = Field(default=None, primary_key=True)
    spray_program_id: int = Field(foreign_key="spray_programs.id", nullable=False)
    chemical_id: int = Field(foreign_key="chemicals.id", nullable=False)
    mix_rate_per_100L: Decimal = Field(
        default=0, max_digits=5, decimal_places=2, nullable=False
    )

    spray_program: SprayProgram = Relationship(back_populates="spray_program_chemicals")
    chemical: "Chemical" = Relationship(back_populates="spray_program_chemicals")


class Chemical(SQLModel, table=True):
    __tablename__ = "chemicals"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    active_ingredient: str

    spray_program_chemicals: list[SprayProgramChemical] = Relationship(
        back_populates="chemical"
    )
