import datetime
from decimal import Decimal
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

        self.date_completed: datetime.date = datetime.date.today()

        self.edit = False

        self.spray = spray_service.eagerly_get_spray_by_id(spray_id, session)

        self.chemicals = vineyard_service.get_spray_chemicals(spray_id, session)
        self.growth_stages = vineyard_service.all_growth_stages(session)
        ic(self.growth_stages)
        ic("################################################")
        ic(self.date_completed)

        self.spray_records: list[SprayRecord] = (
            vineyard_service.eagerly_get_vineyard_spray_spray_records(
                self.session, self.vineyard_id, spray_id
            )
        )
        self.wind_directions = list(WindDirection)

        self.operator_id: int | None = None
        self.growth_stage_id: int | None = None
        self.hours_taken: Decimal | None = None
        self.temperature: int | None = None
        self.relative_humidity: int | None = None
        self.wind_speed: str | None = None
        self.wind_direction: int | None = None
        self.management_unit_ids: List[int] | None = None
        self.form = None
