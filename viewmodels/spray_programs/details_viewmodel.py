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
