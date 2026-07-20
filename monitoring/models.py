import datetime
import enum
from typing import TYPE_CHECKING, List, Optional

import sqlalchemy as sa
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from data.user import User
    from data.vineyard import GrowthStage, ManagementUnit


class MonitoringSeason(SQLModel, table=True):
    """
    Represents a monitoring season, e.g. "2025/2026".
    """

    __tablename__ = "monitoring_seasons"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False, unique=True)  # e.g. "2025/2026"
    season_start: datetime.date = Field(nullable=False, index=True)
    season_end: datetime.date = Field(nullable=False, index=True)

    is_current: bool = Field(default=False, index=True)
    is_archived: bool = Field(default=False, index=True)

    notes: Optional[str] = Field(default=None)

    date_created: datetime.datetime = Field(
        sa_column=sa.Column(sa.DateTime, default=datetime.datetime.now, index=True)
    )

    # Relationships
    monitoring_records: List["MonitoringRecord"] = Relationship(
        back_populates="season",
        cascade_delete=True,
    )

    def __str__(self) -> str:
        return self.name


class MonitoringRecord(SQLModel, table=True):
    __tablename__ = "monitoring_records"

    id: int | None = Field(default=None, primary_key=True)

    season_id: int = Field(
        foreign_key="monitoring_seasons.id",
        nullable=False,
        ondelete="CASCADE",
        index=True,
    )

    management_unit_id: int = Field(
        foreign_key="management_units.id",
        index=True,
        nullable=False,
    )

    observer_id: int | None = Field(
        foreign_key="users.id",
        default=None,
        index=True,
    )

    monitoring_date: datetime.date = Field(sa_column=sa.Column(sa.Date, nullable=False))

    growth_stage_id: int | None = Field(
        foreign_key="growth_stages.id",
        default=None,
        index=True,
    )

    date_created: datetime.datetime = Field(
        sa_column=sa.Column(
            sa.DateTime,
            default=datetime.datetime.now,
            index=True,
        )
    )

    date_updated: datetime.datetime = Field(
        sa_column=sa.Column(
            sa.DateTime,
            default=datetime.datetime.now,
            onupdate=datetime.datetime.now,
            index=True,
        )
    )

    season: MonitoringSeason = Relationship(back_populates="monitoring_records")
    management_unit: "ManagementUnit" = Relationship()
    observer: "User" = Relationship()
    growth_stage: "GrowthStage" = Relationship()

    observations: list["Observation"] = Relationship(
        back_populates="monitoring_record",
        cascade_delete=True,
    )


class ObservationCategory(str, enum.Enum):
    DISEASE = "Disease"

    SNAIL = "Snail"

    MITE = "Mite"

    CATERPILLAR = "Caterpillar"

    INSECT = "Insect"

    ANIMAL = "Animal"

    BENEFICIAL = "Beneficial"

    GENERAL = "General"


class ObservationTarget(str, enum.Enum):
    # =========================
    # Diseases - Powdery Mildew
    # =========================

    POWDERY_FLAG_SHOOTS = "Flag Shoots"
    POWDERY_LEAVES = "Leaves (powdery)"
    POWDERY_BUNCHES = "Bunches"
    POWDERY_BERRIES = "Berries"

    # =========================
    # Diseases - Downy Mildew
    # =========================

    DOWNY_OIL_SPOTS = "Oil Spots (Leaves)"
    DOWNY_LEAVES = "Down (Leaves)"
    DOWNY_BUNCHES = "Bunches (downy)"

    # =========================
    # Diseases - Botrytis / Bunch Rots
    # =========================

    BOTRYTIS_LEAF_LESIONS = "Leaf Lesions"
    BOTRYTIS_SHOOT_LESIONS = "Shoot Lesions"
    BOTRYTIS_BUNCH_DAMAGE = "Bunch Damage"

    # =========================
    # Diseases - Leaf Spot / Phomopsis
    # =========================

    PHOMOPSIS_LEAVES = "Leaves (phomopsis)"
    PHOMOPSIS_SHOOTS = "Shoots"
    PHOMOPSIS_BUNCHES = "Bunches (phomopsis)"
    PHOMOPSIS_CANES = "Canes"

    # =========================
    # Diseases - Other
    # =========================

    DIAPORTHE_SYMPTOMS = "Diaporthe Symptoms"
    LRV_SYMPTOMS = "LRV Symptoms"
    TRUNK_DISEASE_SYMPTOMS = "Trunk Disease Symptoms"
    AUSTRALIAN_GRAPEVINE_YELLOWS = "Australian Grapevine Yellows"
    SCLEROTINIA_SYMPTOMS = "Sclerotinia Symptoms"

    # =========================
    # Snails
    # =========================

    GARDEN_SNAIL = "Garden Snail"
    CONE_SNAIL = "Cone Snail"
    ITALIAN_SNAIL = "Italian Snail"

    # =========================
    # Weevils
    # =========================

    WEEVILS = "Weevils"

    # =========================
    # Mites
    # =========================

    BUD_MITE_SYMPTOMS = "Bud Mite Symptoms"
    RUST_MITE_SYMPTOMS = "Rust Mite Symptoms"
    BLISTER_MITE_SYMPTOMS = "Blister Mite Symptoms"

    # =========================
    # Mealy Bug
    # =========================

    MEALY_TRUNK_CORDON = "Trunk / Cordon"
    MEALY_LEAVES = "Leaves (mealy)"
    MEALY_SOOTY_MOULD = "Sooty Mould"

    # =========================
    # Caterpillars
    # =========================

    LIGHT_BROWN_APPLE_MOTH = "Light Brown Apple Moth"
    LOOPER = "Looper"
    GRAPEVINE_MOTH = "Grapevine Moth"
    HELIOTHIS = "Heliothis"
    OTHER_CATERPILLAR = "Other Caterpillar"

    # =========================
    # Other Insects
    # =========================

    SPRING_BEETLE = "Spring Beetle"
    BLACK_BEETLE = "Black Beetle"
    GRASSHOPPERS = "Grasshoppers"
    SCALE = "Scale"
    RUTHERGLEN_BUG = "Rutherglen Bug"

    # =========================
    # Animals
    # =========================

    KANGAROOS = "Kangaroos"

    BIRDS = "Birds"
    RABBITS = "Rabbits"
    OTHER_RODENTS = "Other Rodents"

    # =========================
    # Beneficial Species
    # =========================

    LADYBIRDS = "Ladybirds"
    LACEWINGS = "Lacewings"
    PARASITIC_WASPS = "Parasitic Wasps"
    SPIDERS = "Spiders"
    BEES = "Bees"
    DRAGONFLIES = "Dragonflies"
    PREDATORY_MITES = "Predatory Mites"
    HOVERFLIES = "Hoverflies"
    OTHER_BENEFICIAL = "Other Beneficial"

    # =========================
    # General Observations
    # =========================

    WATER_STRESS = "Water Stress"
    NUTRITION_ISSUE = "Nutrition Issue"
    WIND_DAMAGE = "Wind Damage"
    HAIL_DAMAGE = "Hail Damage"
    MACHINERY_DAMAGE = "Machinery Damage"
    FROST_DAMAGE = "Frost Damage"
    CHEMICAL_BURN = "Chemical Burn"
    DRAINAGE_ISSUE = "Drainage Issue"
    BIRD_NETTING_ISSUE = "Bird Netting Issue"
    HERBICIDE_DAMAGE = "Herbicide Damage"
    OTHER_OBSERVATION = "Other Observation"


class Distribution(str, enum.Enum):
    ISOLATED = "Isolated"
    SCATTERED = "Scattered"
    REGULAR = "Regular"
    WIDESPREAD = "Widespread"


class Pressure(str, enum.Enum):
    NONE = "None"
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    SEVERE = "Severe"


class Severity(str, enum.Enum):
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    SEVERE = "Severe"


class Presence(str, enum.Enum):
    NONE = "None"
    RARE = "Rare"
    OCCASIONAL = "Occasional"
    COMMON = "Common"
    ABUNDANT = "Abundant"


class Activity(str, enum.Enum):
    NONE = "None"
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"


class Damage(str, enum.Enum):
    NONE = "None"
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    SEVERE = "Severe"


class Lifecycle(str, enum.Enum):
    EGG_MASSES = "Egg masses"
    EARLY_INSTARS = "Early instars"
    MID_INSTARS = "Mid instars"
    PUPAE = "Pupae"
    ADULT_MOTHS = "Adult moths"


class Observation(SQLModel, table=True):
    __tablename__ = "observations"

    id: int | None = Field(default=None, primary_key=True)

    monitoring_record_id: int = Field(
        foreign_key="monitoring_records.id",
        nullable=False,
        index=True,
    )

    category: ObservationCategory = Field(
        sa_column=sa.Column(sa.Enum(ObservationCategory))
    )

    target: ObservationTarget = Field(sa_column=sa.Column(sa.Enum(ObservationTarget)))

    presence: Presence | None = Field(
        default=None,
        sa_column=sa.Column(sa.Enum(Presence)),
    )

    severity: Severity | None = Field(
        default=None,
        sa_column=sa.Column(sa.Enum(Severity)),
    )

    pressure: Pressure | None = Field(
        default=None,
        sa_column=sa.Column(sa.Enum(Pressure)),
    )

    distribution: Distribution | None = Field(
        default=None,
        sa_column=sa.Column(sa.Enum(Distribution)),
    )

    damage: Damage | None = Field(
        default=None,
        sa_column=sa.Column(sa.Enum(Damage)),
    )

    activity: Activity | None = Field(
        default=None,
        sa_column=sa.Column(sa.Enum(Activity)),
    )

    lifecycle: Lifecycle | None = Field(
        default=None,
        sa_column=sa.Column(sa.Enum(Lifecycle)),
    )

    description: str | None

    monitoring_record: MonitoringRecord = Relationship(back_populates="observations")

    locations: list["ObservationLocation"] = Relationship(
        back_populates="observation",
        cascade_delete=True,
    )


class ObservationLocationType(str, enum.Enum):
    SOIL = "Soil"
    BASE = "Base"
    TRUNK = "Trunk"
    CROWN = "Crown"
    CANOPY = "Canopy"
    NEW_GROWTH = "New growth"


class ObservationLocation(SQLModel, table=True):
    __tablename__ = "observation_locations"
    __table_args__ = (
        sa.UniqueConstraint(
            "observation_id", "location", name="uq_observation_location"
        ),
    )

    id: int | None = Field(default=None, primary_key=True)

    observation_id: int = Field(
        foreign_key="observations.id",
        nullable=False,
        index=True,
    )

    location: ObservationLocationType = Field(
        sa_column=sa.Column(sa.Enum(ObservationLocationType))
    )

    observation: Observation = Relationship(back_populates="locations")
