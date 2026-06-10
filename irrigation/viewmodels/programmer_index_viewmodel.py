from dataclasses import dataclass, field
from typing import Optional

from sqlmodel import Session, select
from starlette.requests import Request

from data.vineyard import ManagementUnit, Vineyard
from irrigation import irrigation_services
from irrigation.models import IrrigationProgrammingRecord, IrrigationSchedule
from irrigation.viewmodels.irrigation_viewmodel_base import IrrigationViewModelBase


@dataclass
class ProgrammerMURow:
    """
    A single MU row as seen by the programmer — shows the active schedule
    and whether it has been programmed into the controller.
    """

    management_unit: ManagementUnit
    active_schedule: Optional[IrrigationSchedule]
    latest_programming_record: Optional[IrrigationProgrammingRecord]

    @property
    def is_programmed(self) -> bool:
        return self.latest_programming_record is not None

    @property
    def needs_programming(self) -> bool:
        """
        True if there is an active schedule but no programming record for it,
        or if the schedule was created after the last programming record.
        """
        if not self.active_schedule:
            return False
        if not self.latest_programming_record:
            return True
        return (
            self.active_schedule.date_created
            > self.latest_programming_record.date_programmed
        )


@dataclass
class ProgrammerVineyardGroup:
    """
    A vineyard and its MU rows as seen by the programmer.
    """

    vineyard: Vineyard
    rows: list[ProgrammerMURow] = field(default_factory=list)

    @property
    def needs_attention(self) -> bool:
        """True if any MU in this vineyard needs programming."""
        return any(row.needs_programming for row in self.rows)

    @property
    def programmed_count(self) -> int:
        return sum(1 for row in self.rows if row.is_programmed)

    @property
    def total_count(self) -> int:
        return len(self.rows)


class ProgrammerIndexViewModel(IrrigationViewModelBase):
    """
    Programmer's entry point — all vineyards listed with a status indicator
    showing whether their controllers are up to date.

    Vineyards that need attention (unprogrammed schedule changes) are
    visually distinguished from those that are up to date.
    """

    def __init__(self, request: Request, session: Session):
        super().__init__(request, session)

        self.vineyard_groups: list[ProgrammerVineyardGroup] = []

        if not self.current_irrigation_season:
            self.set_warning("No active irrigation season.")
            return

        vineyards = session.exec(select(Vineyard).order_by(Vineyard.name)).all()

        # Load all schedules for this season in one query
        all_schedules = irrigation_services.get_schedules_for_season(
            session, self.current_irrigation_season.id
        )

        # Index active schedules (no effective_until) by MU id
        active_schedules_by_mu: dict[int, IrrigationSchedule] = {
            s.management_unit_id: s for s in all_schedules if s.effective_until is None
        }

        for vineyard in vineyards:
            active_units = [mu for mu in vineyard.management_units if mu.is_active]
            if not active_units:
                continue

            group = ProgrammerVineyardGroup(vineyard=vineyard)

            for mu in sorted(active_units, key=lambda m: m.name):
                active_schedule = active_schedules_by_mu.get(mu.id)

                latest_record = (
                    active_schedule.latest_programming_record
                    if active_schedule
                    else None
                )

                group.rows.append(
                    ProgrammerMURow(
                        management_unit=mu,
                        active_schedule=active_schedule,
                        latest_programming_record=latest_record,
                    )
                )

            self.vineyard_groups.append(group)

        # Surface vineyards needing attention first
        self.vineyard_groups.sort(
            key=lambda g: (not g.needs_attention, g.vineyard.name)
        )
