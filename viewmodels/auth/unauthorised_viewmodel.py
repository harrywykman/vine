from typing import Optional

from fastapi.requests import Request
from sqlmodel import Session

from viewmodels.shared.viewmodel import ViewModelBase


class UnauthorisedViewModel(ViewModelBase):
    def __init__(self, request: Request, session: Session):
        super().__init__(request, session)

        self.message: Optional[str] = None
