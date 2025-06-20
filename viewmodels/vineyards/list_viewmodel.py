from typing import Optional

from data.vineyard import Vineyard
from services import vineyard_service
from starlette.requests import Request
from viewmodels.shared.viewmodel import ViewModelBase


class ListViewModel(ViewModelBase):
    def __init__(self, request: Request):
        super().__init__(request)

        self.vineyards: List[Vineyard] = vineyard_service.all_vineyards()