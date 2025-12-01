import datetime
from decimal import Decimal
from typing import List, Optional

import sqlalchemy as sa
from sqlmodel import Field, Relationship, SQLModel

from data.user import User
from data.vineyard import ManagementUnit

class IrrigationProgram(SQLModel, table=True):
    __tablename__ = "irrigation_programs"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    year_start: int = Field(default=datetime.datetime.now().year, index=True)
    year_end: int = Field(default=datetime.datetime.now().year, index=True)
    date_created: datetime.datetime = Field(
        sa_column=sa.Column(sa.DateTime, default=datetime.datetime.now, index=True)
    )

    # Many-to-many relationship with IrrigationSchedule
    IrrigationSchedule: List["IrrigationSchedule"] = Relationship(back_populates="irrigation_program")

    def __str__(self):
        return f"{self.name} ({self.year_start} / {self.year_end})"


class IrrigationSchedule(SQLModel, table=True):
    __tablename__ = "irrigation_schedules"
    __table_args__ = (
        sa.UniqueConstraint(
            "name", "irrigation_program_id", name="unique_irrigation_schedule_name_per_program"
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)

    date_created: datetime.datetime = Field(
        sa_column=sa.Column(sa.DateTime, default=datetime.datetime.now, index=True)
    )

    applications_per_week: int | None

    hours_per_application: Decimal | None = Field(sa_column=sa.Column(sa.Numeric(2, 1)))

    ideal_schedule_start_date: datetime.datetime | None = Field(
        sa_column=sa.Column(sa.DateTime, default=None, index=True)
    )

    irrigation_program_id: int = Field(
        foreign_key="spray_programs.id", nullable=False, index=True
    )

    irrigation_program: IrrigationProgram = Relationship(back_populates="irrigation_scedule")

    irrigation_schedule_records: List["IrrigationScheduleRecord"] = Relationship(
        back_populates="irrigation_schedule", cascade_delete=True
    )

    def __str__(self):
        return f"{self.name}"


class IrrigationScheduleRecord(SQLModel, table=True):
    __tablename__ = "irrigation_schedule_records"

    id: Optional[int] = Field(default=None, primary_key=True)
    operator_id: int | None = Field(foreign_key="users.id", nullable=True, index=True)
    scheduled: bool | None
    date_created: datetime.datetime = Field(
        sa_column=sa.Column(sa.DateTime, default=datetime.datetime.now, index=True)
    )
    date_scheduled: datetime.datetime | None = Field(
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
    date_ended: datetime.datetime | None = Field(
        sa_column=sa.Column(sa.DateTime, default=None, index=True)
    )

    program_identifier: str | None

    application_start_time: datetime.datetime | None = Field(
        sa_column=sa.Column(sa.DateTime, default=None, index=True)
    )

    management_unit_id: int = Field(
        foreign_key="management_units.id", nullable=False, index=True
    )

    management_unit: ManagementUnit = Relationship(
        back_populates="irrigation_schedule_records"
    )
    operator: "User" = Relationship(back_populates="irrigation_schedule_records")

    def __str__(self):
        return f"{self.scheduled}"

    @property
    def formatted_date_scheduled(self):
        if self.date_scheduled:
            return self.date_scheduled.strftime("%d/%m/%Y")
        return None



#### Models Suggested by Claude ####

import datetime
from decimal import Decimal
from typing import List, Optional

import sqlalchemy as sa
from sqlmodel import Field, Relationship, SQLModel

from data.user import User
from data.vineyard import ManagementUnit


class IrrigationSeason(SQLModel, table=True):
    """
    Represents an irrigation season (e.g., 2024-2025).
    Similar to your IrrigationProgram but renamed for clarity.
    """
    __tablename__ = "irrigation_seasons"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False, unique=True)  # e.g., "2024-2025"
    year_start: int = Field(default=datetime.datetime.now().year, index=True)
    year_end: int = Field(default=datetime.datetime.now().year, index=True)
    
    start_date: datetime.date = Field(nullable=False, index=True)
    end_date: Optional[datetime.date] = Field(default=None, index=True)
    is_active: bool = Field(default=True, index=True)
    
    notes: Optional[str] = Field(default=None)
    
    date_created: datetime.datetime = Field(
        sa_column=sa.Column(sa.DateTime, default=datetime.datetime.now, index=True)
    )

    # Relationships
    schedules: List["IrrigationSchedule"] = Relationship(
        back_populates="season",
        cascade_delete=True
    )

    def __str__(self):
        return f"{self.name}"

    @property
    def is_current(self) -> bool:
        """Check if today falls within this season"""
        today = datetime.date.today()
        if self.end_date:
            return self.start_date <= today <= self.end_date
        return self.start_date <= today and self.is_active


class IrrigationSchedule(SQLModel, table=True):
    """
    A schedule defines the irrigation parameters for a management unit
    during a specific time period within a season.
    """
    __tablename__ = "irrigation_schedules"

    id: Optional[int] = Field(default=None, primary_key=True)
    
    management_unit_id: int = Field(
        foreign_key="management_units.id",
        nullable=False,
        ondelete="CASCADE",
        index=True
    )
    season_id: int = Field(
        foreign_key="irrigation_seasons.id",
        nullable=False,
        ondelete="CASCADE",
        index=True
    )

    # Effective date range for this schedule
    effective_from: datetime.date = Field(nullable=False, index=True)
    effective_until: Optional[datetime.date] = Field(default=None, index=True)

    # Schedule parameters
    applications_per_week: int = Field(default=0)
    duration_hours: Decimal = Field(
        sa_column=sa.Column(sa.Numeric(3, 1)),
        description="Duration in hours per application"
    )

    # Optional: specific days and times
    days_of_week: Optional[str] = Field(
        default=None,
        description="e.g., 'Mon, Wed, Fri' or 'Tue, Thu'"
    )
    start_time: Optional[str] = Field(
        default=None,
        description="e.g., '5:30pm' or '3:00am'"
    )

    # Notes for context
    notes: Optional[str] = Field(default=None)

    # Audit fields
    created_by_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    date_created: datetime.datetime = Field(
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

    # Relationships
    management_unit: ManagementUnit = Relationship(
        back_populates="irrigation_schedules"
    )
    season: IrrigationSeason = Relationship(back_populates="schedules")
    created_by: User = Relationship(foreign_keys=[created_by_id])
    
    programming_records: List["IrrigationProgrammingRecord"] = Relationship(
        back_populates="schedule",
        cascade_delete=True
    )

    def __str__(self):
        return f"{self.management_unit.name} - {self.effective_from.strftime('%d/%m/%Y')}"

    @property
    def schedule_summary(self) -> str:
        """Human-readable schedule summary"""
        if self.applications_per_week == 0:
            return "No irrigation"
        return f"{self.duration_hours}hrs, {self.applications_per_week}x per week"

    @property
    def is_active(self) -> bool:
        """Check if this schedule is currently active"""
        today = datetime.date.today()
        if self.effective_until:
            return self.effective_from <= today < self.effective_until
        return self.effective_from <= today

    @property
    def duration_days(self) -> int:
        """Calculate how many days this schedule was/is in effect"""
        if self.effective_until:
            return (self.effective_until - self.effective_from).days
        
        # If still active, calculate up to today or season end
        end_date = datetime.date.today()
        if self.season.end_date:
            end_date = min(end_date, self.season.end_date)
        
        return max(0, (end_date - self.effective_from).days)

    @property
    def duration_weeks(self) -> Decimal:
        """Duration in weeks (fractional)"""
        return Decimal(self.duration_days) / Decimal(7)

    @property
    def total_hours(self) -> Decimal:
        """Total water hours applied during this schedule period"""
        return (
            self.duration_weeks 
            * Decimal(self.applications_per_week) 
            * self.duration_hours
        )

    @property
    def total_water_volume_ml(self) -> Optional[Decimal]:
        """
        Calculate total water volume in megalitres.
        You'll need to adjust the application rate based on your systems.
        """
        if not self.management_unit.area:
            return None
        
        # Example calculation - adjust based on your irrigation system
        # Typical drip: 10mm per hour = 100,000 L/ha/hour = 0.1 ML/ha/hour
        application_rate_ml_per_ha_per_hour = Decimal("0.1")
        
        volume = (
            self.total_hours 
            * self.management_unit.area 
            * application_rate_ml_per_ha_per_hour
        )
        
        return volume

    @property
    def is_programmed(self) -> bool:
        """Check if this schedule has been programmed into a controller"""
        return any(record.programmed for record in self.programming_records)

    @property
    def latest_programming_record(self) -> Optional["IrrigationProgrammingRecord"]:
        """Get the most recent programming record"""
        if not self.programming_records:
            return None
        return max(self.programming_records, key=lambda r: r.date_programmed)


class IrrigationProgrammingRecord(SQLModel, table=True):
    """
    Records when a schedule was actually programmed into the field controller.
    This is separate from the schedule itself because:
    1. A schedule might be programmed multiple times (corrections, reprogramming)
    2. You want to track WHO programmed it and WHEN
    3. You want to track controller-specific details
    """
    __tablename__ = "irrigation_programming_records"

    id: Optional[int] = Field(default=None, primary_key=True)
    
    schedule_id: int = Field(
        foreign_key="irrigation_schedules.id",
        nullable=False,
        ondelete="CASCADE",
        index=True
    )
    
    programmed_by_id: int = Field(
        foreign_key="users.id",
        nullable=False,
        index=True
    )
    
    programmed: bool = Field(default=True)
    
    date_programmed: datetime.datetime = Field(
        sa_column=sa.Column(sa.DateTime, default=datetime.datetime.now, index=True)
    )
    
    # Controller-specific details
    controller_program_letter: Optional[str] = Field(
        default=None,
        description="Program identifier in the controller (e.g., 'A', 'B', 'C')"
    )
    
    controller_start_time: Optional[str] = Field(
        default=None,
        description="Actual start time programmed (e.g., '5:30pm', '3:00am')"
    )
    
    controller_days: Optional[str] = Field(
        default=None,
        description="Actual days programmed (e.g., 'Tue, Fri')"
    )
    
    # Notes about the programming
    notes: Optional[str] = Field(
        default=None,
        description="Any issues, changes, or observations during programming"
    )
    
    # If this schedule was stopped/ended early
    date_ended: Optional[datetime.datetime] = Field(
        sa_column=sa.Column(sa.DateTime, default=None, index=True),
        description="If this schedule was manually stopped before effective_until"
    )

    # Relationships
    schedule: IrrigationSchedule = Relationship(back_populates="programming_records")
    programmed_by: User = Relationship(back_populates="irrigation_programming_records")

    def __str__(self):
        return f"{self.schedule.management_unit.name} - {self.formatted_date_programmed}"

    @property
    def formatted_date_programmed(self):
        if self.date_programmed:
            return self.date_programmed.strftime("%d/%m/%Y %H:%M")
        return None

    @property
    def controller_details(self) -> str:
        """Human-readable controller programming details"""
        parts = []
        if self.controller_program_letter:
            parts.append(f"Program {self.controller_program_letter}")
        if self.controller_start_time:
            parts.append(f"Start {self.controller_start_time}")
        if self.controller_days:
            parts.append(self.controller_days)
        return " - ".join(parts) if parts else "No details"
    

### Update to ManagementUnit

class ManagementUnit(SQLModel, table=True):
    # ... existing fields ...
    
    irrigation_schedules: List["IrrigationSchedule"] = Relationship(
        back_populates="management_unit"
    )
    
    def get_current_irrigation_schedule(
        self, 
        season_id: Optional[int] = None
    ) -> Optional["IrrigationSchedule"]:
        """Get the currently active irrigation schedule for this unit"""
        today = datetime.date.today()
        
        schedules = [
            s for s in self.irrigation_schedules 
            if s.effective_from <= today
            and (s.effective_until is None or s.effective_until > today)
        ]
        
        if season_id:
            schedules = [s for s in schedules if s.season_id == season_id]
        
        # Return the most recent one
        if schedules:
            return max(schedules, key=lambda s: s.effective_from)
        return None
    
    def get_season_irrigation_hours(self, season_id: int) -> Decimal:
        """Calculate total irrigation hours for this unit in a given season"""
        schedules = [s for s in self.irrigation_schedules if s.season_id == season_id]
        return sum(s.total_hours for s in schedules)
    
    def get_season_water_volume(self, season_id: int) -> Optional[Decimal]:
        """Calculate total water volume (ML) for this unit in a given season"""
        schedules = [s for s in self.irrigation_schedules if s.season_id == season_id]
        volumes = [s.total_water_volume_ml for s in schedules if s.total_water_volume_ml]
        return sum(volumes) if volumes else None
    
### Update to User

class User:
    # ... existing fields ...
    
    irrigation_programming_records: List["IrrigationProgrammingRecord"] = Relationship(
        back_populates="programmed_by"
    )

### Explanation

Key Differences from Your Original

    Renamed IrrigationProgram → IrrigationSeason: More intuitive naming that includes date range
    IrrigationSchedule is simpler: Removed the "name" field (not needed), added effective_from and effective_until for temporal tracking
    Renamed IrrigationScheduleRecord → IrrigationProgrammingRecord: Better describes what it tracks (the physical act of programming controllers)
    Separated concerns:
        Schedule = WHAT to irrigate (parameters)
        Programming Record = WHEN it was programmed and BY WHOM
    Added computed properties: Easy access to totals, status checks, etc.

This structure gives you:

    ✅ Persistent schedules that continue until changed
    ✅ Clear audit trail of who programmed what and when
    ✅ Flexibility to reprogram or correct mistakes
    ✅ Easy calculation of seasonal water usage
    ✅ Simple queries for "what's active now"
