from sqlmodel import Session
from starlette.requests import Request

from data.vineyard import SprayRecord
from services import spray_service, vineyard_service
from viewmodels.shared.viewmodel import ViewModelBase


class VineyardSprayRecordsFormSelectViewModel(ViewModelBase):
    def __init__(
        self,
        vineyard_id: int,
        spray_id: int,
        request: Request,
        session: Session,
    ):
        super().__init__(request, session)

        self.vineyard_id = vineyard_id
        self.spray_id = spray_id
        self.request = request
        self.session = session

        self.spray = spray_service.eagerly_get_spray_by_id(spray_id, session)
        self.spray_records: list[SprayRecord] = (
            vineyard_service.eagerly_get_vineyard_spray_spray_records(
                self.session, self.vineyard_id, spray_id
            )
        )
