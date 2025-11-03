from typing import Optional

from fastapi import HTTPException
from sqlmodel import Session
from starlette.requests import Request

from data.vineyard import SprayRecord, Vineyard
from services import vineyard_service
from viewmodels.shared.viewmodel import ViewModelBase


class VineyardSprayRecordCancelNote(ViewModelBase):
    def __init__(
        self,
        vineyard_id: int,
        spray_record_id: int,
        request: Request,
        session: Session,
    ):
        super().__init__(request, session)

        self.id: int = vineyard_id
        self.name: Optional[str] = None
        self.address: Optional[str] = None
        self.spray_record_id: int = spray_record_id
        self.vineyard: Vineyard = vineyard_service.get_vineyard_by_id(
            self.session, vineyard_id
        )

        self.spray_record = session.get(SprayRecord, spray_record_id)
        if not self.spray_record:
            raise HTTPException(status_code=404, detail="Spray record not found")
