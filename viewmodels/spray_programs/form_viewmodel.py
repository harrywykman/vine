from datetime import datetime

from sqlmodel import Session
from starlette.requests import Request

from viewmodels.shared.viewmodel import ViewModelBase


class FormViewModel(ViewModelBase):
    def __init__(
        self,
        request: Request,
        session: Session,
    ):
        super().__init__(request, session)

        self.id: int = None
        self.name: str = None
        self.year_start: int = datetime.now().year
        self.year_end: int = datetime.now().year + 1
