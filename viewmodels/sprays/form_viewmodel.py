from typing import Optional

from sqlmodel import Session
from starlette.requests import Request

from data.vineyard import SprayProgram
from services import spray_program_service, vineyard_service
from viewmodels.shared.viewmodel import ViewModelBase


class FormViewModel(ViewModelBase):
    def __init__(
        self,
        request: Request,
        session: Session,
        spray_program_id: Optional[int],
    ):
        super().__init__(request, session)

        self.id: int = None
        self.name: str = "Spray Program"
        self.growth_stages: list = vineyard_service.all_growth_stages(session)
        if spray_program_id:
            self.spray_program: SprayProgram = (
                spray_program_service.get_spray_program_by_id(
                    session=session, spray_program_id=spray_program_id
                )
            )
        else:
            self.spray_program: SprayProgram = None
