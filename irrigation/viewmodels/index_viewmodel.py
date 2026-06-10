from sqlmodel import Session
from starlette.requests import Request

from irrigation import irrigation_services
from irrigation.models import IrrigationSeason
from irrigation.viewmodels.irrigation_viewmodel_base import IrrigationViewModelBase


class IrrigationIndexViewModel(IrrigationViewModelBase):
    """
    Season list — the irrigation module's entry point.
    Shows all seasons with the current one highlighted.
    Admins can create a new season from here.
    """

    def __init__(self, request: Request, session: Session):
        super().__init__(request, session)

        self.seasons: list[IrrigationSeason] = (
            irrigation_services.get_all_irrigation_seasons(self.session)
        )
