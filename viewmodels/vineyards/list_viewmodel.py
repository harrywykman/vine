from sqlmodel import Session
from starlette.requests import Request

from data.vineyard import Vineyard
from services import vineyard_service
from viewmodels.shared.viewmodel import ViewModelBase


class ListViewModel(ViewModelBase):
    def __init__(self, request: Request, session: Session):
        super().__init__(request, session)

        self.vineyards: List[Vineyard] = vineyard_service.all_vineyards(session)
