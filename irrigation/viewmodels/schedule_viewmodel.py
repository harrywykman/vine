import datetime
from decimal import Decimal
from typing import Optional

from sqlmodel import Session
from starlette.requests import Request

from data.vineyard import ManagementUnit
from irrigation import irrigation_services
from irrigation.models import EmitterConfiguration, IrrigationSchedule
from irrigation.viewmodels.irrigation_viewmodel_base import IrrigationViewModelBase


class ScheduleViewModel(IrrigationViewModelBase):
    """
    Planner's form for adding a new schedule or editing an existing one
    for a single management unit.

    For a new schedule:
        ScheduleViewModel(management_unit_id=x, request=request, session=session)

    For editing an existing schedule (correction only — not a new schedule):
        ScheduleViewModel(management_unit_id=x, schedule_id=y, request=request, session=session)
    """

    def __init__(
        self,
        management_unit_id: int,
        request: Request,
        session: Session,
        schedule_id: Optional[int] = None,
    ):
        super().__init__(request, session)

        self.management_unit: Optional[ManagementUnit] = session.get(
            ManagementUnit, management_unit_id
        )

        if not self.management_unit:
            self.set_error("Management unit not found.")
            return

        # Existing schedule being edited, if any
        self.schedule: Optional[IrrigationSchedule] = (
            session.get(IrrigationSchedule, schedule_id) if schedule_id else None
        )

        # Current emitter configuration — shown for reference in the form
        self.emitter_config: Optional[EmitterConfiguration] = (
            irrigation_services.get_current_emitter_config(session, management_unit_id)
        )

        # Schedule history for this MU in the current season — shown below the form
        self.schedule_history: list[IrrigationSchedule] = (
            irrigation_services.get_schedules_for_management_unit(
                session,
                management_unit_id,
                self.current_irrigation_season.id,
            )
            if self.current_irrigation_season
            else []
        )

        # Form field defaults — pre-populated from existing schedule if editing
        self.effective_from: Optional[datetime.date] = (
            self.schedule.effective_from if self.schedule else datetime.date.today()
        )
        self.effective_until: Optional[datetime.date] = (
            self.schedule.effective_until if self.schedule else None
        )
        self.applications_per_week: Optional[int] = (
            self.schedule.applications_per_week if self.schedule else None
        )
        self.duration_hours: Optional[Decimal] = (
            self.schedule.duration_hours if self.schedule else None
        )
        self.notes: Optional[str] = self.schedule.notes if self.schedule else None

        self.is_edit = self.schedule is not None
