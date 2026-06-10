from sqlmodel import Session
from starlette.requests import Request

from irrigation import irrigation_services
from irrigation.models import IrrigationSeason
from viewmodels.shared.viewmodel import ViewModelBase


class IrrigationViewModelBase(ViewModelBase):
    """
    Base viewmodel for all irrigation views.

    Inherits user, auth, and spray season context from ViewModelBase,
    and adds irrigation season resolution using the same cookie pattern.

    Cookie key: "viewing_irrigation_season_id"
    - Present: load that archived season
    - Absent: load the current active irrigation season
    """

    def __init__(self, request: Request, session: Session):
        super().__init__(request, session)

        viewing_irrigation_season_id = request.cookies.get(
            "viewing_irrigation_season_id"
        )

        if viewing_irrigation_season_id:
            self.current_irrigation_season: IrrigationSeason | None = (
                irrigation_services.get_irrigation_season_by_id(
                    self.session, int(viewing_irrigation_season_id)
                )
            )
            self.is_viewing_irrigation_archive = True
        else:
            self.current_irrigation_season: IrrigationSeason | None = (
                irrigation_services.get_current_irrigation_season(self.session)
            )
            self.is_viewing_irrigation_archive = False
