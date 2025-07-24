from fastapi import HTTPException
from sqlmodel import Session
from starlette.requests import Request

from services import spray_service, vineyard_service
from viewmodels.shared.viewmodel import ViewModelBase


class ApplySelectMUsFormViewModel(ViewModelBase):
    def __init__(self, spray_id: int, request: Request, session: Session):
        super().__init__(request, session)

        self.spray = spray_service.eagerly_get_spray_by_id(spray_id, session)
        if not self.spray:
            raise HTTPException(status_code=404, detail="Spray not found")

        self.vineyards = vineyard_service.all_vineyards_with_mangement_units(
            session=session
        )


class SelectFormViewModel(ViewModelBase):
    def __init__(self, vineyard_id: int, request: Request, session: Session):
        super().__init__(request, session)

        self.vineyard = vineyard_service.get_vineyard_by_id(
            session=session, id=vineyard_id
        )
