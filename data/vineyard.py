import datetime
import enum
from decimal import Decimal
from typing import List, Optional

import sqlalchemy as sa
from sqlmodel import Field, Relationship, SQLModel

###### CORE VINEYARD MODELS ########


class Vineyard(SQLModel, table=True):
    __tablename__ = "vineyards"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    address: Optional[str] = Field(default=None)

    management_units: List["ManagementUnit"] = Relationship(back_populates="vineyard")


class Variety(SQLModel, table=True):
    __tablename__ = "varieties"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)  # e.g. "Cabernet Sauvignon"
    wine_colour_id: int = Field(foreign_key="wine_colours.id")

    wine_colour: "WineColour" = Relationship(back_populates="varieties")
    management_units: List["ManagementUnit"] = Relationship(back_populates="variety")


class Status(SQLModel, table=True):
    __tablename__ = "states"

    id: Optional[int] = Field(default=None, primary_key=True)
    status: str = Field(default="Active")

    management_units: List["ManagementUnit"] = Relationship(back_populates="status")


class ManagementUnit(SQLModel, table=True):
    __tablename__ = "management_units"

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

    spray_records: List["SprayRecord"] = Relationship(back_populates="management_unit")

    variety_id: int | None = Field(default=None, foreign_key="varieties.id")
    vineyard_id: int | None = Field(default=None, foreign_key="vineyards.id")
    status_id: int | None = Field(default=None, foreign_key="states.id")

    variety: Variety | None = Relationship(back_populates="management_units")
    vineyard: Vineyard | None = Relationship(back_populates="management_units")
    status: Status | None = Relationship(back_populates="management_units")


class WineColour(SQLModel, table=True):
    __tablename__ = "wine_colours"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)  # e.g. "Red", "White"

    varieties: List["Variety"] = Relationship(back_populates="wine_colour")


###### SPRAY RELATED MODELS ########


class GrowthStage(SQLModel, table=True):
    __tablename__ = "growth_stages"

    id: Optional[int] = Field(default=None, primary_key=True)
    el_number: int = Field(
        index=True,
        nullable=False,
        unique=True,
        description="EL stage number (Eichhorn-Lorenz)",
    )
    description: str = Field(
        nullable=False, description="Description of the growth stage"
    )
    is_major: bool = Field(
        default=False,
        description="Indicates whether the stage is a major phenological phase",
    )


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

    spray_program_chemicals: List["SprayProgramChemical"] = Relationship(
        back_populates="spray_program", cascade_delete=True
    )
    spray_records: List["SprayRecord"] = Relationship(
        back_populates="spray_program", cascade_delete=True
    )


class SprayRecord(SQLModel, table=True):
    __tablename__ = "spray_records"

    id: Optional[int] = Field(default=None, primary_key=True)
    operator: str | None
    complete: bool | None
    date_created: datetime.datetime = Field(
        sa_column=sa.Column(sa.DateTime, default=datetime.datetime.now, index=True)
    )
    # TODO: Add Growth Stage

    management_unit_id: int = Field(foreign_key="management_units.id", nullable=False)
    spray_program_id: int = Field(
        foreign_key="spray_programs.id", nullable=False, ondelete="CASCADE"
    )

    management_unit: ManagementUnit = Relationship(back_populates="spray_records")
    spray_program: SprayProgram = Relationship(back_populates="spray_records")


class Target(str, enum.Enum):
    RUST_MITE = "Rust mite (if present)"
    BUD_MITE = "Bud mite (if present)"
    BOTRYTIS = "Botrytis"
    DOWNY_MILDEW = "Downy mildew"
    NUTRITION = "Nutrition"
    POWDERY_BOT = "Powdery / Botrytis"
    POWDERY = "Powdery mildew"
    WETTER = "Wetter"


class SprayProgramChemical(SQLModel, table=True):
    __tablename__ = "spray_program_chemicals"

    id: Optional[int] = Field(default=None, primary_key=True)
    spray_program_id: int = Field(
        foreign_key="spray_programs.id", nullable=False, ondelete="CASCADE"
    )
    chemical_id: int = Field(foreign_key="chemicals.id", nullable=False)
    mix_rate_per_100L: Decimal = Field(
        default=0, max_digits=5, decimal_places=2, nullable=False
    )
    target: Optional[Target] = Field(default=None, sa_column=sa.Column(sa.Enum(Target)))

    spray_program: SprayProgram = Relationship(back_populates="spray_program_chemicals")
    chemical: "Chemical" = Relationship(back_populates="spray_program_chemicals")


class ChemicalGroupLink(SQLModel, table=True):
    __tablename__ = "chemical_group_link"
    __table_args__ = {"extend_existing": True}

    chemical_id: Optional[int] = Field(
        default=None, foreign_key="chemicals.id", primary_key=True
    )
    group_id: Optional[int] = Field(
        default=None, foreign_key="chemical_groups.id", primary_key=True
    )


class ChemicalGroupType(str, enum.Enum):
    FUNGICIDE = "Fungicide"
    HERBICIDE = "Herbicide"
    INSECTICIDE = "Insecticide"
    OTHER = "Other"


class ChemicalGroup(SQLModel, table=True):
    __tablename__ = "chemical_groups"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(
        index=True,
        description="Descriptive name of the chemical group (e.g. 'Group 3 (DMI)')",
    )
    code: str | None = Field(
        index=True,
        nullable=False,
        unique=True,
        description="Group code (e.g. '3', 'B', 'M')",
    )
    type: Optional[ChemicalGroupType] = Field(
        sa_column_kwargs={"nullable": False},
        description="Type of pesticide (Fungicide, Herbicide, Insecticide, etc.)",
    )
    moa: str | None = Field(
        nullable=False, description="Mode of action (e.g. 'Demethylation inhibitors')"
    )

    # Backref to linked chemicals (many-to-many via ChemicalGroupLink)
    chemicals: Optional[List["Chemical"]] = Relationship(
        back_populates="chemical_groups", link_model=ChemicalGroupLink
    )

    def __str__(self):
        return f"{self.code} – {self.name}"


class MixRateUnit(str, enum.Enum):
    MILLILITRES = "ml"
    GRAMS = "g"


class Chemical(SQLModel, table=True):
    __tablename__ = "chemicals"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    active_ingredient: str
    rate_per_100l: Optional[int] = None
    rate_unit: Optional[MixRateUnit] = Field(
        default=None, sa_column=sa.Column(sa.Enum(MixRateUnit))
    )

    chemical_groups: List[ChemicalGroup] | None = Relationship(
        back_populates="chemicals", link_model=ChemicalGroupLink
    )

    spray_program_chemicals: List["SprayProgramChemical"] = Relationship(
        back_populates="chemical"
    )
