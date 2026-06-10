from dataclasses import dataclass, field
from typing import Optional

from sqlmodel import Session, select
from starlette.requests import Request

from data.vineyard import ManagementUnit, Vineyard
from irrigation import irrigation_services
from irrigation.models import IrrigationSchedule
from irrigation.viewmodels.irrigation_viewmodel_base import IrrigationViewModelBase


@dataclass
class ManagementUnitRow:
    """
    All the data the planner grid needs for a single MU row.
    """

    management_unit: ManagementUnit
    active_schedule: Optional[IrrigationSchedule]
    schedule_history: list[IrrigationSchedule]

    @property
    def has_active_schedule(self) -> bool:
        return self.active_schedule is not None

    @property
    def is_irrigated(self) -> bool:
        """True if the active schedule has a non-zero application rate."""
        return (
            self.active_schedule is not None
            and self.active_schedule.applications_per_week > 0
        )


@dataclass
class VineyardGroup:
    """
    A vineyard and its MU rows, as displayed in the planner grid.
    """

    vineyard: Vineyard
    rows: list[ManagementUnitRow] = field(default_factory=list)

    @property
    def has_any_active_schedules(self) -> bool:
        return any(row.has_active_schedule for row in self.rows)


class IrrigationSeasonViewModel(IrrigationViewModelBase):
    """
    Planner grid — all vineyards grouped, each with their active MUs as rows.
    Each row shows the current schedule and links to add or edit a schedule.

    Defaults to the current irrigation season; falls back gracefully if
    no season exists yet.
    """

    def __init__(self, request: Request, session: Session):
        super().__init__(request, session)

        self.vineyard_groups: list[VineyardGroup] = []

        if not self.current_irrigation_season:
            self.set_warning("No active irrigation season. Please create one.")
            return

        # Load all active vineyards with their active management units
        vineyards = session.exec(select(Vineyard).order_by(Vineyard.name)).all()

        # Load all schedules for this season in one query to avoid N+1
        all_schedules = irrigation_services.get_schedules_for_season(
            session, self.current_irrigation_season.id
        )

        # Index schedules by management_unit_id for fast lookup
        schedules_by_mu: dict[int, list[IrrigationSchedule]] = {}
        for schedule in all_schedules:
            schedules_by_mu.setdefault(schedule.management_unit_id, []).append(schedule)

        for vineyard in vineyards:
            active_units = [mu for mu in vineyard.management_units if mu.is_active]
            if not active_units:
                continue

            group = VineyardGroup(vineyard=vineyard)

            for mu in sorted(active_units, key=lambda m: m.name):
                mu_schedules = schedules_by_mu.get(mu.id, [])

                # Active schedule — the one with no effective_until
                active_schedule = next(
                    (s for s in mu_schedules if s.effective_until is None), None
                )

                # History — closed schedules, most recent first
                history = sorted(
                    [s for s in mu_schedules if s.effective_until is not None],
                    key=lambda s: s.effective_from,
                    reverse=True,
                )

                group.rows.append(
                    ManagementUnitRow(
                        management_unit=mu,
                        active_schedule=active_schedule,
                        schedule_history=history,
                    )
                )

            self.vineyard_groups.append(group)
