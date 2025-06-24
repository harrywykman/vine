from sqlmodel import Session
from starlette.requests import Request

from data.vineyard import ManagementUnit
from services import vineyard_service
from viewmodels.shared.viewmodel import ViewModelBase


class EditMUViewModel(ViewModelBase):
    def __init__(self, management_unit_id: int, request: Request, session: Session):
        super().__init__(request, session)

        self.id: int = management_unit_id
        self.mu: ManagementUnit = vineyard_service.eagerly_get_management_unit_by_id(
            self.session, management_unit_id
        )
        self.varieties = vineyard_service.all_varieties(session)
