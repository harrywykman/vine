import datetime
from typing import Optional

from sqlmodel import Session

from monitoring.models import (
    MonitoringRecord,
    Observation,
    ObservationCategory,
    ObservationTarget,
    Presence,
    Severity,
)


def create_monitoring_record(
    session: Session,
    management_unit_id: int,
    observer_id: Optional[int],
    monitoring_date: datetime.date,
    growth_stage_id: Optional[int] = None,
) -> MonitoringRecord:
    record = MonitoringRecord(
        management_unit_id=management_unit_id,
        observer_id=observer_id,
        monitoring_date=monitoring_date,
        growth_stage_id=growth_stage_id,
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def get_monitoring_record_by_id(
    session: Session, monitoring_record_id: int
) -> Optional[MonitoringRecord]:
    return session.get(MonitoringRecord, monitoring_record_id)


def save_disease_observations(
    session: Session,
    monitoring_record_id: int,
    targets: list[str],
    presences: list[Optional[str]],
    severities: list[Optional[str]],
) -> int:
    """
    Creates one Observation row per disease target where the scout entered
    both presence and severity. Targets left entirely blank (section never
    expanded, or expanded but not filled in) are skipped rather than saved
    as empty rows.

    A target with only one of presence/severity filled in is also skipped
    for now; that's a partial-fill case the form should prevent via
    required-together fields once the disease partial enforces it client-side.

    Returns the number of observations created, so the caller/viewmodel can
    show an accurate success message (e.g. "3 observations recorded").
    """
    created = 0

    for target_value, presence_value, severity_value in zip(
        targets, presences, severities
    ):
        if not presence_value and not severity_value:
            continue
        if not presence_value or not severity_value:
            # Partial fill - skip silently for now rather than reject the
            # whole submission. Revisit once the form enforces this itself.
            continue

        observation = Observation(
            monitoring_record_id=monitoring_record_id,
            category=ObservationCategory.DISEASE,
            target=ObservationTarget(target_value),
            presence=Presence(presence_value),
            severity=Severity(severity_value),
        )
        session.add(observation)
        created += 1

    session.commit()
    return created
