from sqlmodel import Session
from starlette.requests import Request

from services import vineyard_service
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
        self.growth_stages: list = vineyard_service.all_growth_stages(session)
