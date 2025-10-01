import datetime
import enum
from decimal import Decimal
from typing import List, Optional

import sqlalchemy as sa
from geoalchemy2 import Geometry
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import Polygon
from sqlmodel import Field, Relationship, SQLModel

from data.user import User

###### CORE VINEYARD MODELS ########


class Vineyard(SQLModel, table=True):
    __tablename__ = "vineyards"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True, nullable=False)
    address: Optional[str] = Field(default=None)
    boundary: Optional[str] = Field(
        default=None,
        sa_column=sa.Column(Geometry("POLYGON", srid=4326)),
        description="Vineyard boundary as a polygon in WGS84 (EPSG:4326)",
    )

    management_units: List["ManagementUnit"] = Relationship(back_populates="vineyard")

    def __str__(self):
        return f"{self.name}"

    @property
    def name_slugified(self):
        return f"{self.name.lower().strip().replace(' ', '-')}"

    @property
    def boundary_coordinates(self):
        """Convert PostGIS geometry to GeoJSON for frontend use"""
        if self.boundary:
            shape = to_shape(self.boundary)

            # Swap coordinates from (lon, lat) to [lat, lon] for Leaflet
            coordinates = [[lat, lon] for lon, lat in shape.exterior.coords]

            return coordinates
        return None

    @property
    def has_active_management_units(self) -> bool:
        """
        Returns True if this vineyard has any active management units.
        """
        return any(unit.is_active for unit in self.management_units)

    @property
    def has_red_wine_units(self) -> bool:
        """
        Returns True if this vineyard has any red wine management units.
        """
        return any(unit.is_red_wine for unit in self.management_units)

    @property
    def has_white_wine_units(self) -> bool:
        """
        Returns True if this vineyard has any white wine management units.
        """
        return any(unit.is_white_wine for unit in self.management_units)

    @property
    def active_management_units_count(self) -> int:
        """
        Returns the count of active management units in this vineyard.
        """
        return sum(1 for unit in self.management_units if unit.is_active)

    @property
    def total_management_units_count(self) -> int:
        """
        Returns the total count of management units in this vineyard.
        """
        return len(self.management_units)

    @property
    def centroid(self):
        """Calculate the centroid of the vineyard boundary for Leaflet setView"""
        if self.boundary:
            try:
                from geoalchemy2.shape import to_shape

                # Convert WKBElement to Shapely geometry and get centroid
                shape = to_shape(self.boundary)
                centroid_point = shape.centroid

                # Return as [latitude, longitude] for Leaflet setView
                return [centroid_point.y, centroid_point.x]

            except Exception as e:
                print(f"Error calculating centroid: {e}")
                print(f"Boundary type: {type(self.boundary)}")

        # Fallback to hardcoded coordinates
        return []

    def set_boundary_from_coordinates(self, coordinates: List[List[float]]):
        """Set boundary from list of [lng, lat] coordinates"""
        if coordinates and len(coordinates) >= 3:
            # Ensure the polygon is closed
            if coordinates[0] != coordinates[-1]:
                coordinates.append(coordinates[0])

            polygon = Polygon(coordinates)
            self.boundary = from_shape(polygon, srid=4326)


class Variety(SQLModel, table=True):
    __tablename__ = "varieties"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)  # e.g. "Cabernet Sauvignon"
    wine_colour_id: int = Field(foreign_key="wine_colours.id", index=True)

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

    # PostGIS polygon field for management unit area
    area_polygon: Optional[str] = Field(
        default=None,
        sa_column=sa.Column(Geometry("POLYGON", srid=4326)),
        description="Management unit area as a polygon in WGS84 (EPSG:4326)",
    )

    spray_records: List["SprayRecord"] = Relationship(back_populates="management_unit")

    variety_id: int | None = Field(default=None, foreign_key="varieties.id", index=True)
    vineyard_id: int | None = Field(
        default=None, foreign_key="vineyards.id", ondelete="CASCADE", index=True
    )
    status_id: int | None = Field(default=None, foreign_key="states.id", index=True)

    variety: Variety | None = Relationship(back_populates="management_units")
    vineyard: Vineyard | None = Relationship(back_populates="management_units")
    status: Status | None = Relationship(back_populates="management_units")

    def __str__(self):
        return f"{self.name}"

    @property
    def is_active(self):
        return self.status.status == "Active"

    @property
    def name_with_variety(self):
        if self.name and self.variety:
            return f"{self.name} - {self.variety.name}"
        elif self.name:
            return f"{self.name}"

    @property
    def area_coordinates_lat_long(self):
        """Convert PostGIS geometry to GeoJSON for frontend use"""
        if self.area_polygon:
            shape = to_shape(self.area_polygon)

            # Swap coordinates from (lon, lat) to [lat, lon] for Leaflet
            coordinates = [[lat, lon] for lon, lat in shape.exterior.coords]

            return coordinates
        return None

    def set_area_polygon_from_coordinates(self, coordinates: List[List[float]]):
        """Set area polygon from list of [lng, lat] coordinates"""
        if coordinates and len(coordinates) >= 3:
            # Ensure the polygon is closed
            if coordinates[0] != coordinates[-1]:
                coordinates.append(coordinates[0])

            polygon = Polygon(coordinates)
            self.area_polygon = from_shape(polygon, srid=4326)

    @property
    def is_red_wine(self) -> bool:
        """
        Returns True if this management unit grows red wine varieties.
        """
        return (
            self.variety
            and self.variety.wine_colour
            and self.variety.wine_colour.is_red()
        )

    @property
    def is_white_wine(self) -> bool:
        """
        Returns True if this management unit grows white wine varieties.
        """
        return (
            self.variety
            and self.variety.wine_colour
            and self.variety.wine_colour.is_white()
        )

    @property
    def has_wine_colour(self) -> bool:
        """
        Returns True if this management unit has a variety with a defined wine colour.
        """
        return self.variety and self.variety.wine_colour is not None

    @property
    def wine_bottle_tooltip(self) -> str:
        """
        Returns a tooltip description for the wine bottle icon.
        """
        if not self.is_active:
            return (
                f"Inactive - {self.variety.name if self.variety else 'Unknown variety'}"
            )

        if self.variety and self.variety.wine_colour:
            return f"{self.variety.wine_colour.name} wine - {self.variety.name}"

        return "Active management unit"


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
    year_start: int = Field(default=datetime.datetime.now().year, index=True)
    year_end: int = Field(default=datetime.datetime.now().year, index=True)
    date_created: datetime.datetime = Field(
        sa_column=sa.Column(sa.DateTime, default=datetime.datetime.now, index=True)
    )

    # Many-to-many relationship with Spray
    sprays: List["Spray"] = Relationship(back_populates="spray_program")

    def __str__(self):
        return f"{self.name} ({self.year_start} / {self.year_end})"


class Spray(SQLModel, table=True):
    __tablename__ = "sprays"
    __table_args__ = (
        sa.UniqueConstraint(
            "name", "spray_program_id", name="unique_spray_name_per_program"
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    water_spray_rate_per_hectare: int

    date_created: datetime.datetime = Field(
        sa_column=sa.Column(sa.DateTime, default=datetime.datetime.now, index=True)
    )

    growth_stage_id: int | None = Field(foreign_key="growth_stages.id", index=True)

    spray_program_id: int = Field(
        foreign_key="spray_programs.id", nullable=False, index=True
    )

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

    @property
    def has_completed_spray_records(self) -> bool:
        """
        Returns True if this spray has at least one completed spray record.
        """
        return any(
            record.complete
            for record in self.spray_records
            if record.complete is not None
        )

    @property
    def spray_chemicals_sorted(self) -> List["SprayChemical"]:
        """
        Returns spray chemicals sorted by their ID.
        """
        return sorted(self.spray_chemicals, key=lambda x: x.id)


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
    operator_id: int | None = Field(foreign_key="users.id", nullable=True, index=True)
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
    growth_stage_id: int | None = Field(foreign_key="growth_stages.id", index=True)
    growth_stage: GrowthStage = Relationship(back_populates="spray_records")
    hours_taken: Decimal | None = Field(sa_column=sa.Column(sa.Numeric(2, 1)))

    spray_start_time: datetime.datetime | None = Field(
        sa_column=sa.Column(sa.DateTime, default=None, index=True)
    )
    spray_finish_time: datetime.datetime | None = Field(
        sa_column=sa.Column(sa.DateTime, default=None, index=True)
    )

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
    operator: "User" = Relationship(back_populates="spray_records")
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
    GROWTH = "Growth Regulator"


class SprayChemical(SQLModel, table=True):
    __tablename__ = "spray_chemicals"
    __table_args__ = (
        sa.UniqueConstraint("spray_id", "chemical_id", name="uq_spray_chemical"),
        {"extend_existing": True},
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    spray_id: int = Field(
        foreign_key="sprays.id", nullable=False, ondelete="CASCADE", index=True
    )
    chemical_id: int = Field(foreign_key="chemicals.id", nullable=False, index=True)
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
        default=None,
        foreign_key="chemicals.id",
        primary_key=True,
        ondelete="CASCADE",
        index=True,
    )
    group_id: Optional[int] = Field(
        default=None,
        foreign_key="chemical_groups.id",
        primary_key=True,
        ondelete="CASCADE",
        index=True,
    )


class ChemicalGroupType(str, enum.Enum):
    FUNGICIDE = "Fungicide"
    HERBICIDE = "Herbicide"
    INSECTICIDE = "Insecticide"
    OTHER = "Other"
    NON = "Non"


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


class ChemicalActiveIngredientLink(SQLModel, table=True):
    __tablename__ = "chemical_active_ingredient_link"

    chemical_id: Optional[int] = Field(
        default=None,
        foreign_key="chemicals.id",
        primary_key=True,
        ondelete="CASCADE",
        index=True,
    )
    active_ingredient_id: Optional[int] = Field(
        default=None,
        foreign_key="active_ingredients.id",
        primary_key=True,
        ondelete="CASCADE",
        index=True,
    )


class ActiveIngredientUnit(str, enum.Enum):
    GL = "g/L"
    GKG = "g/kg"


class ActiveIngredient(SQLModel, table=True):
    __tablename__ = "active_ingredients"

    id: int = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    max_el_id: int | None = Field(
        foreign_key="growth_stages.id", nullable=True, ondelete="CASCADE", index=True
    )

    min_days_before_harvest: int | None

    chemicals: List["Chemical"] | None = Relationship(
        back_populates="active_ingredients", link_model=ChemicalActiveIngredientLink
    )


class ChemicalReentryLink(SQLModel, table=True):
    __tablename__ = "chemical_reentry_link"

    chemical_id: Optional[int] = Field(
        default=None,
        foreign_key="chemicals.id",
        primary_key=True,
        ondelete="CASCADE",
        index=True,
    )
    reentry_id: Optional[int] = Field(
        default=None,
        foreign_key="reentry_period.id",
        primary_key=True,
        ondelete="CASCADE",
        index=True,
    )


class ReentryPeriod(SQLModel, table=True):
    __tablename__ = "reentry_period"

    id: int = Field(default=None, primary_key=True)
    letter_code: str = Field(
        index=True,
        description="letter code for re-entry period",
    )
    description: str

    chemicals: List["Chemical"] | None = Relationship(
        back_populates="reentry_periods", link_model=ChemicalReentryLink
    )


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

    reentry_periods: List[ReentryPeriod] | None = Relationship(
        back_populates="chemicals", link_model=ChemicalReentryLink
    )

    active_ingredients: List[ActiveIngredient] | None = Relationship(
        back_populates="chemicals", link_model=ChemicalActiveIngredientLink
    )

    active_ingredient_unit: Optional[ActiveIngredientUnit] = Field(
        default=None, sa_column=sa.Column(sa.Enum(ActiveIngredientUnit))
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
