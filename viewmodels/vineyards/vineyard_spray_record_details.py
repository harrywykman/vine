from sqlmodel import Session
from starlette.requests import Request

from data.vineyard import SprayRecord
from services import vineyard_service
from viewmodels.shared.viewmodel import ViewModelBase


class VineyardSprayRecordDetail(ViewModelBase):
    def __init__(
        self,
        spray_record_id: int,
        request: Request,
        session: Session,
    ):
        super().__init__(request, session)
        self.spray_record_id = spray_record_id
        self.request = request
        self.session = session

        self.spray_record: SprayRecord | None = (
            vineyard_service.eagerly_get_spray_record_by_id(
                self.session, spray_record_id
            )
        )

        if not self.spray_record:
            self.error = "No spray record found"
