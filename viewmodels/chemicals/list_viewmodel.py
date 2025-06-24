from sqlmodel import Session
from starlette.requests import Request

from data.vineyard import Chemical
from services import chemical_service
from viewmodels.shared.viewmodel import ViewModelBase


class ListViewModel(ViewModelBase):
    def __init__(self, request: Request, session: Session):
        super().__init__(request, session)

        self.chemicals: list[Chemical] = chemical_service.all_chemicals(session)
