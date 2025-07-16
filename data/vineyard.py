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
    name: str = Field(index=True, unique=True, nullable=False)
    address: Optional[str] = Field(default=None)

    management_units: List["ManagementUnit"] = Relationship(back_populates="vineyard")

    def __str__(self):
        return f"{self.name}"


class Variety(SQLModel, table=True):
    __tablename__ = "varieties"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)  # e.g. "Cabernet Sauvignon"
    wine_colour_id: int = Field(foreign_key="wine_colours.id")

    wine_colour: "WineColour" = Relationship(back_populates="varieties")
    management_units: List["ManagementUnit"] = Relationship(back_populates="variety")

    def __str__(self):
        return f"{self.name}"


class Status(SQLModel, table=True):
    __tablename__ = "states"

    id: Optional[int] = Field(default=None, primary_key=True)
    status: str = Field(default="Active")

    management_units: List["ManagementUnit"] = Relationship(back_populates="status")

    def __str__(self):
        return f"{self.status}"


class ManagementUnit(SQLModel, table=True):
    __tablename__ = "management_units"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    variety_name_modifier: Optional[str] = Field(default=None)

    area: Decimal = Field(sa_column=sa.Column(sa.Numeric(5, 2)))
    row_width: Decimal = Field(sa_column=sa.Column(sa.Numeric(2, 1)))
    vine_spacing: Decimal = Field(sa_column=sa.Column(sa.Numeric(2, 1)))

    rows_total: Optional[int] = Field(default=None)
    rows_start_number: Optional[int] = Field(default=None)
    rows_end_number: Optional[int] = Field(default=None)
    date_planted: datetime.datetime | None = Field(sa_column=sa.Column(sa.Date))

    spray_records: List["SprayRecord"] = Relationship(back_populates="management_unit")

    variety_id: int | None = Field(default=None, foreign_key="varieties.id")
    vineyard_id: int | None = Field(
        default=None, foreign_key="vineyards.id", ondelete="CASCADE"
    )
    status_id: int | None = Field(default=None, foreign_key="states.id")

    variety: Variety | None = Relationship(back_populates="management_units")
    vineyard: Vineyard | None = Relationship(back_populates="management_units")
    status: Status | None = Relationship(back_populates="management_units")

    def __str__(self):
        return f"{self.name}"

    @property
    def name_with_variety(self):
        if self.variety:
            return f"{self.name} - {self.variety.name}"
        return None


class WineColour(SQLModel, table=True):
    __tablename__ = "wine_colours"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)  # e.g. "Red", "White"

    varieties: List["Variety"] = Relationship(back_populates="wine_colour")

    def __str__(self):
        return f"{self.name}"

    def is_red(self):
        return self.name == "Red"

    def is_white(self):
        return self.name == "White"


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

    sprays: List["Spray"] = Relationship(back_populates="growth_stage")
    spray_records: List["SprayRecord"] = Relationship(back_populates="growth_stage")

    def __str__(self):
        return f"{self.el_number} - {self.description}"


class SprayProgram(SQLModel, table=True):
    __tablename__ = "spray_programs"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    year: int = Field(default=datetime.datetime.now().year, index=True)
    date_created: datetime.datetime = Field(
        sa_column=sa.Column(sa.DateTime, default=datetime.datetime.now, index=True)
    )

    # Relationships
    sprays: List["Spray"] = Relationship(
        back_populates="spray_program", cascade_delete=True
    )

    def __str__(self):
        return f"{self.name} ({self.year})"


# Many-to-many association table for Spray and SprayProgram
class SprayProgramSprayLink(SQLModel, table=True):
    __tablename__ = "spray_program_spray_links"

    spray_program_id: Optional[int] = Field(
        default=None,
        foreign_key="spray_programs.id",
        primary_key=True,
        ondelete="CASCADE",
    )
    spray_id: Optional[int] = Field(
        default=None, foreign_key="sprays.id", primary_key=True, ondelete="CASCADE"
    )


# Renamed from SprayProgram to Spray
class Spray(SQLModel, table=True):
    __tablename__ = "sprays"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    water_spray_rate_per_hectare: int

    date_created: datetime.datetime = Field(
        sa_column=sa.Column(sa.DateTime, default=datetime.datetime.now, index=True)
    )

    growth_stage_id: int | None = Field(foreign_key="growth_stages.id")
    spray_program_id: int = Field(foreign_key="spray_programs.id", nullable=False)

    growth_stage: GrowthStage = Relationship(back_populates="sprays")
    spray_program: SprayProgram = Relationship(back_populates="sprays")

    spray_chemicals: List["SprayChemical"] = Relationship(
        back_populates="spray", cascade_delete=True
    )
    spray_records: List["SprayRecord"] = Relationship(
        back_populates="spray", cascade_delete=True
    )

    def __str__(self):
        return f"{self.name}"


class WindDirection(str, enum.Enum):
    N = "North"
    NNE = "North-Northeast"
    NE = "Northeast"
    ENE = "East-Northeast"
    E = "East"
    ESE = "East-Southeast"
    SE = "Southeast"
    SSE = "South-Southeast"
    S = "South"
    SSW = "South-Southwest"
    SW = "Southwest"
    WSW = "West-Southwest"
    W = "West"
    WNW = "West-Northwest"
    NW = "Northwest"
    NNW = "North-Northwest"


class SprayRecord(SQLModel, table=True):
    __tablename__ = "spray_records"

    id: Optional[int] = Field(default=None, primary_key=True)
    operator: str | None
    complete: bool | None
    date_created: datetime.datetime = Field(
        sa_column=sa.Column(sa.DateTime, default=datetime.datetime.now, index=True)
    )
    date_completed: datetime.datetime | None = Field(
        sa_column=sa.Column(sa.DateTime, default=datetime.datetime.now, index=True)
    )
    date_updated: datetime.datetime = Field(
        sa_column=sa.Column(
            sa.DateTime,
            default=datetime.datetime.now,
            onupdate=datetime.datetime.now,
            index=True,
        )
    )
    growth_stage_id: int | None = Field(foreign_key="growth_stages.id")
    growth_stage: GrowthStage = Relationship(back_populates="spray_records")
    hours_taken: Decimal | None = Field(sa_column=sa.Column(sa.Numeric(2, 1)))

    temperature: int | None
    relative_humidity: int | None

    wind_speed: int | None

    wind_direction: Optional[WindDirection] = Field(
        default=None, sa_column=sa.Column(sa.Enum(WindDirection))
    )

    management_unit_id: int = Field(
        foreign_key="management_units.id", nullable=False, index=True
    )
    spray_id: int = Field(
        foreign_key="sprays.id", nullable=False, ondelete="CASCADE", index=True
    )

    management_unit: ManagementUnit = Relationship(back_populates="spray_records")
    spray: Spray = Relationship(back_populates="spray_records")

    spray_record_chemicals: List["SprayRecordChemical"] | None = Relationship(
        back_populates="spray_record", cascade_delete=True
    )

    def __str__(self):
        return f"{self.complete}"

    @property
    def formatted_date_completed(self):
        if self.date_completed:
            return self.date_completed.strftime("%d/%m/%Y")
        return None


class SprayRecordChemical(SQLModel, table=True):
    __tablename__ = "spray_record_chemicals"
    __table_args__ = (
        sa.UniqueConstraint(
            "spray_record_id", "chemical_id", name="uq_sprayrecord_chemical"
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    spray_record_id: int | None = Field(
        foreign_key="spray_records.id", nullable=False, ondelete="CASCADE"
    )
    chemical_id: int | None = Field(foreign_key="chemicals.id", nullable=False)
    batch_number: str | None

    spray_record: SprayRecord = Relationship(back_populates="spray_record_chemicals")
    chemical: "Chemical" = Relationship(back_populates="spray_record_chemicals")

    def __str__(self):
        return f"batch - {self.batch_number}"


class Target(str, enum.Enum):
    RUST_MITE = "Rust mite (if present)"
    BUD_MITE = "Bud mite (if present)"
    BOTRYTIS = "Botrytis"
    DOWNY_MILDEW = "Downy mildew"
    NUTRITION = "Nutrition"
    POWDERY_BOT = "Powdery / Botrytis"
    POWDERY = "Powdery mildew"
    WETTER = "Wetter"


# Renamed from SprayProgramChemical to SprayChemical
class SprayChemical(SQLModel, table=True):
    __tablename__ = "spray_chemicals"
    __table_args__ = (
        sa.UniqueConstraint("spray_id", "chemical_id", name="uq_spray_chemical"),
        {"extend_existing": True},
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    spray_id: int = Field(foreign_key="sprays.id", nullable=False, ondelete="CASCADE")
    chemical_id: int = Field(foreign_key="chemicals.id", nullable=False)
    concentration_factor: Decimal = Field(
        default=1.00, max_digits=3, decimal_places=2, nullable=False
    )
    target: Optional[Target] = Field(default=None, sa_column=sa.Column(sa.Enum(Target)))

    spray: Spray = Relationship(back_populates="spray_chemicals")
    chemical: "Chemical" = Relationship(back_populates="spray_chemicals")

    def __str__(self):
        return f"Targeting {self.target.value} with concentration factor: {self.concentration_factor}"

    def calculated_mix_rate_per_100L(self):
        return str(int(self.chemical.rate_per_100l * self.concentration_factor))


class ChemicalGroupLink(SQLModel, table=True):
    __tablename__ = "chemical_group_link"
    __table_args__ = {"extend_existing": True}

    chemical_id: Optional[int] = Field(
        default=None, foreign_key="chemicals.id", primary_key=True, ondelete="CASCADE"
    )
    group_id: Optional[int] = Field(
        default=None,
        foreign_key="chemical_groups.id",
        primary_key=True,
        ondelete="CASCADE",
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
    MILLILITRES = "mL"
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

    spray_chemicals: List["SprayChemical"] = Relationship(back_populates="chemical")

    spray_record_chemicals: List["SprayRecordChemical"] = Relationship(
        back_populates="chemical"
    )

    def __str__(self):
        return f"{self.name}"
