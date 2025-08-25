from typing import List

from icecream import ic
from sqlmodel import Session
from starlette.requests import Request

from data.user import User, UserRole
from data.vineyard import SprayRecord, WindDirection
from services import spray_record_service, user_service, vineyard_service
from viewmodels.shared.viewmodel import ViewModelBase


class VineyardSprayRecordsFormEditViewModel(ViewModelBase):
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
        self.operators: List[User] = user_service.get_users_by_role(
            session=session, role=UserRole.OPERATOR
        )

        self.edit = True

        self.spray_record = spray_record_service.eagerly_get_spray_record_by_id(
            session=session, id=spray_record_id
        )
        self.date_completed = self.spray_record.date_completed.date()

        self.growth_stages = vineyard_service.all_growth_stages(session)
        ic(self.growth_stages)
        ic("################################################")
        ic(self.date_completed)

        self.spray_records: list[SprayRecord] = (
            vineyard_service.eagerly_get_vineyard_spray_spray_records(
                self.session, self.vineyard_id, self.spray_record.spray.id
            )
        )
        self.wind_directions = list(WindDirection)
