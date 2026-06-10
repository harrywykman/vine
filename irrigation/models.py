import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

import sqlalchemy as sa
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from data.user import User
    from data.vineyard import ManagementUnit


class IrrigationSeason(SQLModel, table=True):
    """
    Represents an irrigation season, e.g. "2025/2026".
    """

    __tablename__ = "irrigation_seasons"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False, unique=True)  # e.g. "2025/2026"
    season_start: datetime.date = Field(nullable=False, index=True)
    season_end: datetime.date = Field(nullable=False, index=True)

    # Stored flags — consistent with SpraySeason, allows efficient filtering
    is_current: bool = Field(default=False, index=True)
    is_archived: bool = Field(default=False, index=True)

    notes: Optional[str] = Field(default=None)

    date_created: datetime.datetime = Field(
        sa_column=sa.Column(sa.DateTime, default=datetime.datetime.now, index=True)
    )

    # Relationships
    schedules: List["IrrigationSchedule"] = Relationship(
        back_populates="season",
        cascade_delete=True,
    )

    def __str__(self) -> str:
        return self.name


class IrrigationSchedule(SQLModel, table=True):
    """
    A standing schedule for a management unit within a season.

    A new row is created only when the schedule changes. effective_until is
    set automatically by the service layer when a new schedule supersedes
    this one (to match the new schedule's effective_from), or manually when
    a controller is turned off without a replacement schedule.

    effective_until = None means the schedule is still running.

    Season volume is the sum of each schedule's contribution:
        days_active = (effective_until - effective_from).days
        weeks_active = days_active / 7
        total_hours = weeks_active * applications_per_week * duration_hours
        volume_m3 = volume_per_hour(emitter_config) * total_hours
    """

    __tablename__ = "irrigation_schedules"

    id: Optional[int] = Field(default=None, primary_key=True)

    management_unit_id: int = Field(
        foreign_key="management_units.id",
        nullable=False,
        ondelete="CASCADE",
        index=True,
    )
    season_id: int = Field(
        foreign_key="irrigation_seasons.id",
        nullable=False,
        ondelete="CASCADE",
        index=True,
    )

    effective_from: datetime.date = Field(nullable=False, index=True)

    # Set by the service layer when a new schedule supersedes this one,
    # or manually when the controller is turned off. None = still running.
    effective_until: Optional[datetime.date] = Field(default=None, index=True)

    # Core schedule parameters
    applications_per_week: int = Field(default=0)
    duration_hours: Decimal = Field(
        sa_column=sa.Column(
            sa.Numeric(3, 1),
            nullable=False,
        ),
        description="Hours per application, e.g. 1.5, 2.0, 0.5",
    )

    # Planner notes — e.g. context for the schedule change
    notes: Optional[str] = Field(default=None)

    # Audit
    created_by_id: Optional[int] = Field(
        default=None,
        foreign_key="users.id",
        index=True,
    )
    date_created: datetime.datetime = Field(
        sa_column=sa.Column(sa.DateTime, default=datetime.datetime.now, index=True)
    )

    # Relationships
    season: IrrigationSeason = Relationship(back_populates="schedules")
    management_unit: Optional["ManagementUnit"] = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[IrrigationSchedule.management_unit_id]",
            "lazy": "select",
        }
    )
    created_by: Optional["User"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[IrrigationSchedule.created_by_id]"}
    )
    programming_records: List["IrrigationProgrammingRecord"] = Relationship(
        back_populates="schedule",
        cascade_delete=True,
    )

    def __str__(self) -> str:
        return (
            f"{self.management_unit.name} — "
            f"from {self.effective_from.strftime('%d/%m/%Y')}"
        )

    @property
    def schedule_summary(self) -> str:
        """Human-readable summary matching the spreadsheet convention."""
        if self.applications_per_week == 0:
            return "No irrigation"
        return f"{self.duration_hours}hrs × {self.applications_per_week}/week"

    @property
    def is_zero(self) -> bool:
        """True if this is an explicit 'no irrigation' schedule."""
        return self.applications_per_week == 0

    @property
    def latest_programming_record(self) -> Optional["IrrigationProgrammingRecord"]:
        """Most recent programming record, if any."""
        if not self.programming_records:
            return None
        return max(self.programming_records, key=lambda r: r.date_programmed)

    @property
    def is_programmed(self) -> bool:
        """True if this schedule has at least one programming record."""
        return bool(self.programming_records)


class IrrigationProgrammingRecord(SQLModel, table=True):
    """
    Records a physical visit to program a schedule into an irrigation
    controller. Separate from the schedule because:

    - A schedule may persist across many weeks but the controller is only
      visited when something changes.
    - A schedule may be reprogrammed more than once (corrections, faults).
    - The controller-specific details (program letter, start time, days)

    """

    __tablename__ = "irrigation_programming_records"

    id: Optional[int] = Field(default=None, primary_key=True)

    schedule_id: int = Field(
        foreign_key="irrigation_schedules.id",
        nullable=False,
        ondelete="CASCADE",
        index=True,
    )

    programmed_by_id: Optional[int] = Field(
        default=None,
        foreign_key="users.id",
        index=True,
    )

    date_programmed: datetime.datetime = Field(
        sa_column=sa.Column(sa.DateTime, default=datetime.datetime.now, index=True)
    )

    # e.g. "5:30pm, Tues/Fri" — free text matching real-world notation
    controller_note: Optional[str] = Field(default=None)

    # Any issues or observations during the visit
    notes: Optional[str] = Field(default=None)

    # Relationships
    schedule: IrrigationSchedule = Relationship(back_populates="programming_records")
    programmed_by: Optional["User"] = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[IrrigationProgrammingRecord.programmed_by_id]"
        }
    )

    def __str__(self) -> str:
        return (
            f"{self.schedule.management_unit.name} — "
            f"programmed {self.formatted_date_programmed}"
        )

    @property
    def formatted_date_programmed(self) -> str:
        if self.date_programmed:
            return self.date_programmed.strftime("%d/%m/%Y %H:%M")
        return "—"

    @property
    def controller_details(self) -> str:
        return self.controller_note if self.controller_note else "No details recorded"


class EmitterConfiguration(SQLModel, table=True):
    """
    Records the drip emitter specification for a management unit.

    A new row is added whenever the emitter system changes — previous rows
    are never modified. The active configuration for any given date is the
    most recent row with effective_from <= that date.


    Volume per hour for a management unit:
        emitters_per_ha  = 10,000 / (emitter_spacing_m × row_width_m)
        total_emitters   = emitters_per_ha × area_ha
        volume_lph       = total_emitters × flow_rate_lph
    """

    __tablename__ = "emitter_configurations"

    id: Optional[int] = Field(default=None, primary_key=True)

    management_unit_id: int = Field(
        foreign_key="management_units.id",
        nullable=False,
        ondelete="CASCADE",
        index=True,
    )

    effective_from: datetime.date = Field(nullable=False, index=True)

    # Distance between emitters along the row, in metres
    emitter_spacing_m: Decimal = Field(
        sa_column=sa.Column(sa.Numeric(4, 2), nullable=False),
        description="Spacing between emitters along the row, in metres",
    )

    # Flow rate per individual emitter, in litres per hour
    flow_rate_lph: Decimal = Field(
        sa_column=sa.Column(sa.Numeric(6, 2), nullable=False),
        description="Flow rate per emitter in litres per hour",
    )

    notes: Optional[str] = Field(
        default=None,
        description="e.g. 'Upgraded to 2.3 L/h emitters after replumbing block 3'",
    )

    recorded_by_id: Optional[int] = Field(
        default=None,
        foreign_key="users.id",
        index=True,
    )
    date_created: datetime.datetime = Field(
        sa_column=sa.Column(sa.DateTime, default=datetime.datetime.now, index=True)
    )

    # Relationships
    management_unit: Optional["ManagementUnit"] = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[EmitterConfiguration.management_unit_id]",
            "lazy": "select",
        }
    )
    recorded_by: Optional["User"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[EmitterConfiguration.recorded_by_id]"}
    )

    def __str__(self) -> str:
        return (
            f"{self.management_unit.name} — "
            f"{self.emitter_spacing_m}m spacing, "
            f"{self.flow_rate_lph} L/h, "
            f"from {self.effective_from.strftime('%d/%m/%Y')}"
        )

    def emitters_per_ha(self, row_width_m: Decimal) -> Decimal:
        """
        Calculate emitter density given the management unit's inter-row spacing.
        row_width_m comes from ManagementUnit.row_width.
        """
        return Decimal(10000) / (self.emitter_spacing_m * row_width_m)

    def volume_per_hour(self, area_ha: Decimal, row_width_m: Decimal) -> Decimal:
        """
        Total volume in m³ per hour for the entire management unit.
        """
        return (self.emitters_per_ha(row_width_m) * self.flow_rate_lph / 1000) * area_ha
