from typing import Optional

from sqlmodel import Session
from starlette.requests import Request

from data.vineyard import ManagementUnit, SprayProgram, SprayRecord, Vineyard
from services import vineyard_service
from viewmodels.shared.viewmodel import ViewModelBase


class DetailsViewModel(ViewModelBase):
    def __init__(self, vineyard_id: int, request: Request, session: Session):
        super().__init__(request, session)

        self.id: int = vineyard_id
        self.name: Optional[str] = None
        self.address: Optional[str] = None
        self.vineyard: Vineyard = vineyard_service.get_vineyard_by_id(
            self.session, vineyard_id
        )

        self.management_units: Optional(List[ManagementUnit]) = (
            vineyard_service.eagerly_get_vineyard_managment_units_by_id(
                self.session, self.id
            )
        )

        self.spray_programs: list[SprayProgram] = (
            vineyard_service.eagerly_get_vineyard_spray_programs(self.session, self.id)
        )

        self.spray_records: list[SprayRecord] = (
            vineyard_service.eagerly_get_vineyard_spray_records(self.session, self.id)
        )

        # Add spray program completion status as a dictionary
        # This creates a mapping of spray_program_id -> completion_status
        self.spray_program_completion_status: dict[int, bool] = {}
        for spray_program in self.spray_programs:
            self.spray_program_completion_status[spray_program.id] = (
                vineyard_service.spray_program_complete_for_vineyard(
                    self.session, spray_program.id, self.id
                )
            )
