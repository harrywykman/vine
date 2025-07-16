from sqlmodel import Session
from starlette.requests import Request

from viewmodels.shared.viewmodel import ViewModelBase


class DetailsViewModel(ViewModelBase):
    def __init__(self, spray_id: int, request: Request, session: Session):
        super().__init__(request, session)

        self.id: int = spray_id
        self.name: str = None
