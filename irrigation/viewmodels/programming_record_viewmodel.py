from dataclasses import dataclass
from typing import Optional

from sqlmodel import Session
from starlette.requests import Request

from data.vineyard import ManagementUnit, Vineyard
from irrigation import irrigation_services
from irrigation.models import IrrigationProgrammingRecord, IrrigationSchedule
from irrigation.viewmodels.irrigation_viewmodel_base import IrrigationViewModelBase


@dataclass
class ProgrammingFormRow:
    """
    One row in the programmer's form — one MU with its active schedule
    and a slot to record controller details.
    """

    management_unit: ManagementUnit
    active_schedule: Optional[IrrigationSchedule]
    latest_programming_record: Optional[IrrigationProgrammingRecord]

    @property
    def schedule_summary(self) -> str:
        if not self.active_schedule:
            return "No schedule set"
        return self.active_schedule.schedule_summary

    @property
    def last_programmed_details(self) -> str:
        if not self.latest_programming_record:
            return "Not yet programmed"
        return self.latest_programming_record.controller_details


class ProgrammingRecordViewModel(IrrigationViewModelBase):
    """
    Programmer's form for a single vineyard — lists all active MUs with
    their current schedules and allows the programmer to record what was
    entered into each controller.

    One form submission covers all MUs in the vineyard in one visit,
    matching the real-world workflow of going to a vineyard and programming
    all its controllers in one trip.
    """

    def __init__(
        self,
        vineyard_id: int,
        request: Request,
        session: Session,
    ):
        super().__init__(request, session)

        self.vineyard: Optional[Vineyard] = session.get(Vineyard, vineyard_id)

        if not self.vineyard:
            self.set_error("Vineyard not found.")
            return

        if not self.current_irrigation_season:
            self.set_error("No active irrigation season.")
            return

        # Load all schedules for this season in one query
        all_schedules = irrigation_services.get_schedules_for_season(
            session, self.current_irrigation_season.id
        )

        # Index active schedules by MU id
        active_schedules_by_mu: dict[int, IrrigationSchedule] = {
            s.management_unit_id: s for s in all_schedules if s.effective_until is None
        }

        active_units = [mu for mu in self.vineyard.management_units if mu.is_active]

        self.rows: list[ProgrammingFormRow] = []

        for mu in sorted(active_units, key=lambda m: m.name):
            active_schedule = active_schedules_by_mu.get(mu.id)
            latest_record = (
                active_schedule.latest_programming_record if active_schedule else None
            )
            self.rows.append(
                ProgrammingFormRow(
                    management_unit=mu,
                    active_schedule=active_schedule,
                    latest_programming_record=latest_record,
                )
            )

        self.vineyard_id = vineyard_id
