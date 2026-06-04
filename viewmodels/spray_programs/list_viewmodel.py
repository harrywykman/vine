from sqlmodel import Session
from starlette.requests import Request

from data.vineyard import SprayProgram
from viewmodels.shared.viewmodel import ViewModelBase


class ListViewModel(ViewModelBase):
    def __init__(self, request: Request, session: Session):
        super().__init__(request, session)

        self.spray_programs: list[SprayProgram] = self.current_spray_programs
