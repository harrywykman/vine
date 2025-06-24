import datetime
from decimal import Decimal
from typing import Optional

import sqlalchemy as sa
from sqlmodel import Field, Relationship, SQLModel

from data.vineyard import ManagementUnit


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

    program_chemicals: list["SprayProgramChemical"] = Relationship(
        back_populates="spray_program"
    )
    spray_records: list["SprayRecord"] = Relationship(back_populates="spray_program")
    management_units: list[ManagementUnit] = Relationship(
        secondary="spray_records",
        back_populates="spray_programs",
        viewonly=True,
    )


class SprayRecord(SQLModel, table=True):
    __tablename__ = "spray_records"

    id: Optional[int] = Field(default=None, primary_key=True)
    operator: str
    complete: bool
    date_created: datetime.datetime = Field(
        sa_column=sa.Column(sa.DateTime, default=datetime.datetime.now, index=True)
    )
    # TODO: Add Growth Stage

    management_unit_id: int = Field(foreign_key="spray_units.id", nullable=False)
    spray_program_id = Field(foreign_key="spray_programs.id", nullable=False)

    management_unit: ManagementUnit = Relationship(back_populates="spray_records")
    spray_program: SprayProgram = Relationship(back_populates="spray_records")

    spray_program_chemicals: list["SprayProgramChemical"] = Relationship(
        back_populates="chemical"
    )


class SprayProgramChemical(SQLModel, table=True):
    __tablename__ = "spray_program_chemicals"

    id: Optional[int] = Field(default=None, primary_key=True)
    spray_program_id = Field(foreign_key="spray_programs.id", nullable=False)
    chemical_id = Field(foreign_key="chemicals.id", nullable=False)
    mix_rate_per_100L = Decimal = Field(
        default=0, max_digits=5, decimal_places=2, nullable=False
    )

    spray_program: SprayProgram = Relationship(back_populates="program_chemicals")
    chemical: Chemical = Relationship(back_populates="program_chemicals")


class Chemical(SQLModel, table=True):
    __tablename__ = "chemicals"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    active_ingredient: str

    spray_program_chemicals: list[SprayProgramChemical] = Relationship(
        back_populates="chemical"
    )
