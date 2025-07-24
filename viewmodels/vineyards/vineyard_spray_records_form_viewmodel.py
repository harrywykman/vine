from typing import List

from icecream import ic
from sqlmodel import Session
from starlette.requests import Request

from data.user import User, UserRole
from data.vineyard import SprayRecord, WindDirection
from services import spray_service, user_service, vineyard_service
from viewmodels.shared.viewmodel import ViewModelBase


class VineyardSprayRecordsFormViewModel(ViewModelBase):
    def __init__(
        self,
        vineyard_id: int,
        spray_id: int,
        request: Request,
        session: Session,
    ):
        super().__init__(request, session)
        self.operator: User | None = user_service.get_user_by_id(
            self.session, self.user_id
        )
        self.vineyard_id = vineyard_id
        self.spray_id = spray_id
        self.request = request
        self.session = session
        self.operators: List[User] = user_service.get_users_by_role(
            session=session, role=UserRole.OPERATOR
        )

        self.edit = False

        self.spray = spray_service.eagerly_get_spray_by_id(spray_id, session)

        self.chemicals = vineyard_service.get_spray_chemicals(spray_id, session)
        self.growth_stages = vineyard_service.all_growth_stages(session)
        ic(self.growth_stages)

        self.spray_records: list[SprayRecord] = (
            vineyard_service.eagerly_get_vineyard_spray_spray_records(
                self.session, self.vineyard_id, spray_id
            )
        )
        self.wind_directions = list(WindDirection)


""" class VineyardSprayRecordsFormViewModel(ViewModelBase):
    def __init__(
        self,
        vineyard_id: int,
        spray_id: int,
        request: Request,
        session: Session,
    ):
        super().__init__(request, session)

        self.id: int = vineyard_id
        self.vineyard: Vineyard = vineyard_service.get_vineyard_by_id(
            self.session, vineyard_id
        )

        self.spray = spray_service.eagerly_get_spray_by_id(
            spray_id, self.session
        )

        self.management_units: Optional(List[ManagementUnit]) = (
            vineyard_service.eagerly_get_vineyard_managment_units_by_id(
                self.session, self.id
            )
        )

        self.spray_records: list[SprayRecord] = (
            vineyard_service.eagerly_get_vineyard_spray_spray_records(
                self.session, self.id, spray_id
            )
        ) """
