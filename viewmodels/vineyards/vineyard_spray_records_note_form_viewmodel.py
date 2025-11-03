from sqlmodel import Session
from starlette.requests import Request

from data.user import User
from services import spray_record_service, user_service
from viewmodels.shared.viewmodel import ViewModelBase


class VineyardSprayRecordsNoteForm(ViewModelBase):
    def __init__(
        self,
        vineyard_id: int,
        spray_record_id: int,
        request: Request,
        session: Session,
    ):
        super().__init__(request, session)
        self.operator: User | None = user_service.get_user_by_id(
            self.session, self.user_id
        )
        self.vineyard_id = vineyard_id
        self.spray_record_id = spray_record_id
        self.request = request
        self.session = session

        self.spray_record = spray_record_service.eagerly_get_spray_record_by_id(
            session=session, id=spray_record_id
        )
