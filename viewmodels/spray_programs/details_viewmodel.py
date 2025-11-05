from icecream import ic
from sqlmodel import Session
from starlette.requests import Request

from data.vineyard import Spray, SprayProgram
from services import spray_program_service
from viewmodels.shared.viewmodel import ViewModelBase


class DetailsViewModel(ViewModelBase):
    def __init__(
        self,
        request: Request,
        session: Session,
        spray_program_id: int,
    ):
        super().__init__(request, session)
        self.spray_program: SprayProgram = (
            spray_program_service.get_spray_program_by_id(
                session=session, spray_program_id=spray_program_id
            )
        )
        self.sprays: list[Spray] = (
            spray_program_service.eagerly_get_all_spray_program_sprays(
                session=session, spray_program_id=self.spray_program.id
            )
        )
        ic(self.sprays)
        self.active_sprays = self._get_active_sprays()
        self.completed_sprays = self._get_completed_sprays()

    def _get_active_sprays(self) -> list[Spray]:
        """Returns sprays that have incomplete spray records or no spray records."""
        return [
            spray
            for spray in self.sprays
            if not spray.spray_records  # No spray records yet
            or not all(
                sr.complete for sr in spray.spray_records
            )  # Any incomplete record
        ]

    def _get_completed_sprays(self) -> list[Spray]:
        """Returns sprays where all spray records are marked as complete."""
        return [
            spray
            for spray in self.sprays
            if spray.spray_records  # Has spray records
            and all(
                sr.complete for sr in spray.spray_records
            )  # ALL records are complete (True)
        ]
