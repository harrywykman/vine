import datetime
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from sqlmodel import Session
from starlette.requests import Request

from data.vineyard import ManagementUnit
from irrigation import irrigation_services
from irrigation.models import EmitterConfiguration, IrrigationSchedule
from irrigation.viewmodels.irrigation_viewmodel_base import IrrigationViewModelBase


@dataclass
class ScheduleHistoryRow:
    """A single schedule row with its volume contribution if closed."""

    schedule: IrrigationSchedule
    volume_m3: Optional[Decimal]

    @property
    def is_active(self) -> bool:
        return self.schedule.effective_until is None

    @property
    def days_active(self) -> Optional[int]:
        if self.schedule.effective_until is None:
            return None
        return (self.schedule.effective_until - self.schedule.effective_from).days


@dataclass
class SeasonStats:
    """Aggregated irrigation statistics for the current season."""

    total_closed_hours: Decimal
    total_volume_m3: Decimal
    schedule_count: int
    has_emitter_config: bool

    @property
    def total_volume_litres(self) -> Decimal:
        return self.total_volume_m3 * 1000

    @property
    def total_volume_ml(self) -> Decimal:
        """Megalitres — useful for larger blocks."""
        return self.total_volume_m3 / 1000


class IrrigationBlockViewModel(IrrigationViewModelBase):
    """
    Detail page for a single management unit's irrigation history.

    Shows:
    - Current emitter configuration and full config history
    - Schedule history for the current season
    - Volume statistics for closed schedules only
    - Form to add a new emitter configuration
    """

    def __init__(
        self,
        management_unit_id: int,
        request: Request,
        session: Session,
    ):
        super().__init__(request, session)

        self.management_unit: Optional[ManagementUnit] = session.get(
            ManagementUnit, management_unit_id
        )

        if not self.management_unit:
            self.set_error("Management unit not found.")
            return

        self.management_unit_id = management_unit_id

        # Emitter configurations — most recent first
        self.emitter_configs: list[EmitterConfiguration] = (
            irrigation_services.get_all_emitter_configs_for_management_unit(
                session, management_unit_id
            )
        )

        self.current_emitter_config: Optional[EmitterConfiguration] = (
            self.emitter_configs[0] if self.emitter_configs else None
        )

        # Schedule history and volume for current season
        self.schedule_rows: list[ScheduleHistoryRow] = []
        self.season_stats: Optional[SeasonStats] = None

        if self.current_irrigation_season:
            schedules = irrigation_services.get_schedules_for_management_unit(
                session,
                management_unit_id,
                self.current_irrigation_season.id,
            )

            total_closed_hours = Decimal(0)
            total_volume_m3 = Decimal(0)

            for schedule in reversed(schedules):  # most recent first
                volume_m3 = None

                if (
                    schedule.effective_until is not None
                    and schedule.applications_per_week > 0
                ):
                    emitter_config = irrigation_services.get_emitter_config_for_date(
                        session, management_unit_id, schedule.effective_from
                    )
                    if (
                        emitter_config
                        and self.management_unit.area
                        and self.management_unit.row_width
                    ):
                        volume_m3 = irrigation_services.calculate_schedule_volume_m3(
                            schedule=schedule,
                            emitter_config=emitter_config,
                            area_ha=self.management_unit.area,
                            row_width_m=self.management_unit.row_width,
                        )
                        days_active = (
                            schedule.effective_until - schedule.effective_from
                        ).days
                        weeks_active = Decimal(days_active) / Decimal(7)
                        total_closed_hours += (
                            weeks_active
                            * Decimal(schedule.applications_per_week)
                            * schedule.duration_hours
                        )
                        total_volume_m3 += volume_m3

                self.schedule_rows.append(
                    ScheduleHistoryRow(schedule=schedule, volume_m3=volume_m3)
                )

            self.season_stats = SeasonStats(
                total_closed_hours=total_closed_hours,
                total_volume_m3=total_volume_m3,
                schedule_count=len(schedules),
                has_emitter_config=self.current_emitter_config is not None,
            )

        # Default effective_from for new emitter config form — today
        self.emitter_config_effective_from = datetime.date.today()
