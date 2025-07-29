from typing import Optional

from sqlmodel import Session, select
from starlette.requests import Request

from data.vineyard import Chemical, SprayProgram, Target
from services import spray_program_service, spray_service, vineyard_service
from viewmodels.shared.viewmodel import ViewModelBase


class EditFormViewModel(ViewModelBase):
    def __init__(
        self,
        request: Request,
        session: Session,
        spray_program_id: Optional[int],
        spray_id: int,
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
        self.spray = spray_service.eagerly_get_spray_by_id(session=session, id=spray_id)
        statement = select(Chemical)
        self.chemicals = session.exec(statement).all()
        self.targets = [target.value for target in Target]
