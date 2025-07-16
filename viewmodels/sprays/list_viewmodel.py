from sqlmodel import Session
from starlette.requests import Request

from data.vineyard import Spray
from services import spray_service
from viewmodels.shared.viewmodel import ViewModelBase


class ListViewModel(ViewModelBase):
    def __init__(self, request: Request, session: Session):
        super().__init__(request, session)

        self.sprays: list[Spray] = spray_service.eagerly_get_all_sprays(session)
