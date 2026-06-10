import datetime
from decimal import Decimal
from typing import Optional

from sqlmodel import Session, select

from irrigation.models import (
    EmitterConfiguration,
    IrrigationProgrammingRecord,
    IrrigationSchedule,
    IrrigationSeason,
)

# ---------------------------------------------------------------------------
# IrrigationSeason
# ---------------------------------------------------------------------------


def get_current_irrigation_season(session: Session) -> Optional[IrrigationSeason]:
    return session.exec(
        select(IrrigationSeason).where(IrrigationSeason.is_current == True)
    ).first()


def get_irrigation_season_by_id(
    session: Session, season_id: int
) -> Optional[IrrigationSeason]:
    return session.get(IrrigationSeason, season_id)


def get_all_irrigation_seasons(session: Session) -> list[IrrigationSeason]:
    return list(
        session.exec(
            select(IrrigationSeason).order_by(IrrigationSeason.season_start.desc())
        ).all()
    )


def create_irrigation_season(
    session: Session,
    name: str,
    season_start: datetime.date,
    season_end: datetime.date,
    notes: Optional[str] = None,
) -> IrrigationSeason:
    """
    Creates a new irrigation season and marks it as current.
    The previously current season is archived automatically.
    """
    # Archive the existing current season
    existing_current = get_current_irrigation_season(session)
    if existing_current:
        existing_current.is_current = False
        existing_current.is_archived = True
        session.add(existing_current)

    season = IrrigationSeason(
        name=name,
        season_start=season_start,
        season_end=season_end,
        is_current=True,
        is_archived=False,
        notes=notes,
    )
    session.add(season)
    session.commit()
    session.refresh(season)
    return season


# ---------------------------------------------------------------------------
# IrrigationSchedule
# ---------------------------------------------------------------------------


def get_schedules_for_season(
    session: Session, season_id: int
) -> list[IrrigationSchedule]:
    """All schedules for a season, ordered by MU then effective_from."""
    return list(
        session.exec(
            select(IrrigationSchedule)
            .where(IrrigationSchedule.season_id == season_id)
            .order_by(
                IrrigationSchedule.management_unit_id,
                IrrigationSchedule.effective_from,
            )
        ).all()
    )


def get_schedules_for_management_unit(
    session: Session, management_unit_id: int, season_id: int
) -> list[IrrigationSchedule]:
    """All schedules for one MU in a season, ordered by effective_from."""
    return list(
        session.exec(
            select(IrrigationSchedule)
            .where(IrrigationSchedule.management_unit_id == management_unit_id)
            .where(IrrigationSchedule.season_id == season_id)
            .order_by(IrrigationSchedule.effective_from)
        ).all()
    )


def get_active_schedule_for_management_unit(
    session: Session, management_unit_id: int, season_id: int
) -> Optional[IrrigationSchedule]:
    """
    The currently active schedule for a MU — the most recent one
    with no effective_until set.
    """
    return session.exec(
        select(IrrigationSchedule)
        .where(IrrigationSchedule.management_unit_id == management_unit_id)
        .where(IrrigationSchedule.season_id == season_id)
        .where(IrrigationSchedule.effective_until == None)
        .order_by(IrrigationSchedule.effective_from.desc())
    ).first()


def get_schedule_by_id(
    session: Session, schedule_id: int
) -> Optional[IrrigationSchedule]:
    return session.get(IrrigationSchedule, schedule_id)


def create_schedule(
    session: Session,
    management_unit_id: int,
    season_id: int,
    effective_from: datetime.date,
    applications_per_week: int,
    duration_hours: Decimal,
    created_by_id: Optional[int] = None,
    notes: Optional[str] = None,
) -> IrrigationSchedule:
    """
    Creates a new schedule for a MU. Automatically closes the previously
    active schedule by setting its effective_until to the new effective_from.
    """
    # Close the currently active schedule for this MU
    active = get_active_schedule_for_management_unit(
        session, management_unit_id, season_id
    )
    if active:
        active.effective_until = effective_from
        session.add(active)

    schedule = IrrigationSchedule(
        management_unit_id=management_unit_id,
        season_id=season_id,
        effective_from=effective_from,
        effective_until=None,
        applications_per_week=applications_per_week,
        duration_hours=duration_hours,
        created_by_id=created_by_id,
        notes=notes,
    )
    session.add(schedule)
    session.commit()
    session.refresh(schedule)
    return schedule


def close_schedule(
    session: Session,
    schedule_id: int,
    effective_until: datetime.date,
) -> Optional[IrrigationSchedule]:
    """
    Explicitly closes a schedule — used when a controller is turned off
    without a replacement schedule being created.
    """
    schedule = get_schedule_by_id(session, schedule_id)
    if not schedule:
        return None
    schedule.effective_until = effective_until
    session.add(schedule)
    session.commit()
    session.refresh(schedule)
    return schedule


def update_schedule(
    session: Session,
    schedule_id: int,
    effective_from: datetime.date,
    applications_per_week: int,
    duration_hours: Decimal,
    effective_until: Optional[datetime.date] = None,
    notes: Optional[str] = None,
) -> Optional[IrrigationSchedule]:
    """
    Updates the parameters of an existing schedule in place.
    Only appropriate for correcting errors — use create_schedule for
    genuine schedule changes so the history is preserved.
    """
    schedule = get_schedule_by_id(session, schedule_id)
    if not schedule:
        return None
    schedule.applications_per_week = applications_per_week
    schedule.duration_hours = duration_hours
    schedule.notes = notes
    schedule.effective_until = effective_until
    schedule.effective_from = effective_from
    session.add(schedule)
    session.commit()
    session.refresh(schedule)
    return schedule


# ---------------------------------------------------------------------------
# IrrigationProgrammingRecord
# ---------------------------------------------------------------------------


def get_programming_records_for_schedule(
    session: Session, schedule_id: int
) -> list[IrrigationProgrammingRecord]:
    return list(
        session.exec(
            select(IrrigationProgrammingRecord)
            .where(IrrigationProgrammingRecord.schedule_id == schedule_id)
            .order_by(IrrigationProgrammingRecord.date_programmed.desc())
        ).all()
    )


def get_programming_record_by_id(
    session: Session, record_id: int
) -> Optional[IrrigationProgrammingRecord]:
    return session.get(IrrigationProgrammingRecord, record_id)


def create_programming_record(
    session: Session,
    schedule_id: int,
    programmed_by_id: Optional[int] = None,
    controller_program_letter: Optional[str] = None,
    controller_note: Optional[str] = None,
    notes: Optional[str] = None,
) -> IrrigationProgrammingRecord:
    record = IrrigationProgrammingRecord(
        schedule_id=schedule_id,
        programmed_by_id=programmed_by_id,
        date_programmed=datetime.datetime.now(),
        controller_program_letter=controller_program_letter,
        controller_note=controller_note,
        notes=notes,
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


# ---------------------------------------------------------------------------
# EmitterConfiguration
# ---------------------------------------------------------------------------


def get_emitter_config_for_date(
    session: Session,
    management_unit_id: int,
    date: datetime.date,
) -> Optional[EmitterConfiguration]:
    """
    Returns the emitter configuration in effect on a given date —
    the most recent configuration with effective_from <= date.
    """
    return session.exec(
        select(EmitterConfiguration)
        .where(EmitterConfiguration.management_unit_id == management_unit_id)
        .where(EmitterConfiguration.effective_from <= date)
        .order_by(EmitterConfiguration.effective_from.desc())
    ).first()


def get_current_emitter_config(
    session: Session, management_unit_id: int
) -> Optional[EmitterConfiguration]:
    return get_emitter_config_for_date(
        session, management_unit_id, datetime.date.today()
    )


def get_all_emitter_configs_for_management_unit(
    session: Session, management_unit_id: int
) -> list[EmitterConfiguration]:
    return list(
        session.exec(
            select(EmitterConfiguration)
            .where(EmitterConfiguration.management_unit_id == management_unit_id)
            .order_by(EmitterConfiguration.effective_from.desc())
        ).all()
    )


def create_emitter_configuration(
    session: Session,
    management_unit_id: int,
    effective_from: datetime.date,
    emitter_spacing_m: Decimal,
    flow_rate_lph: Decimal,
    recorded_by_id: Optional[int] = None,
    notes: Optional[str] = None,
) -> EmitterConfiguration:
    config = EmitterConfiguration(
        management_unit_id=management_unit_id,
        effective_from=effective_from,
        emitter_spacing_m=emitter_spacing_m,
        flow_rate_lph=flow_rate_lph,
        recorded_by_id=recorded_by_id,
        notes=notes,
    )
    session.add(config)
    session.commit()
    session.refresh(config)
    return config


# ---------------------------------------------------------------------------
# Volume calculations
# ---------------------------------------------------------------------------


def calculate_schedule_volume_m3(
    schedule: IrrigationSchedule,
    emitter_config: EmitterConfiguration,
    area_ha: Decimal,
    row_width_m: Decimal,
) -> Decimal:
    """
    Volume in m³ delivered during a single closed schedule period.

    Requires effective_until to be set — open schedules (still running)
    are excluded from volume calculations until closed or the season ends.

        days_active  = (effective_until - effective_from).days
        weeks_active = days_active / 7
        total_hours  = weeks_active × applications_per_week × duration_hours
        volume_m3    = volume_per_hour(emitter_config) × total_hours
    """
    if schedule.effective_until is None:
        return Decimal(0)

    if schedule.applications_per_week == 0:
        return Decimal(0)

    days_active = (schedule.effective_until - schedule.effective_from).days
    if days_active <= 0:
        return Decimal(0)

    weeks_active = Decimal(days_active) / Decimal(7)
    total_hours = (
        weeks_active * Decimal(schedule.applications_per_week) * schedule.duration_hours
    )
    volume_per_hour = emitter_config.volume_per_hour(area_ha, row_width_m)

    return volume_per_hour * total_hours


def calculate_season_volume_for_management_unit(
    session: Session,
    management_unit_id: int,
    season_id: int,
    area_ha: Decimal,
    row_width_m: Decimal,
) -> Decimal:
    """
    Total volume in m³ delivered to a management unit across a full season.
    Only closed schedules (effective_until set) contribute — the currently
    active schedule is excluded until it is closed or the season ends.
    """
    schedules = get_schedules_for_management_unit(
        session, management_unit_id, season_id
    )
    total = Decimal(0)

    for schedule in schedules:
        if schedule.effective_until is None:
            continue

        emitter_config = get_emitter_config_for_date(
            session, management_unit_id, schedule.effective_from
        )
        if emitter_config is None:
            continue

        total += calculate_schedule_volume_m3(
            schedule, emitter_config, area_ha, row_width_m
        )

    return total
