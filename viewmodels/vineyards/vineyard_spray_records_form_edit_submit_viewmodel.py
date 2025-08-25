import datetime
from decimal import Decimal
from typing import List

from fastapi import Request
from icecream import ic
from sqlmodel import Session, select

from data.user import User, UserRole
from data.vineyard import (
    SprayChemical,
    SprayRecord,
    WindDirection,
)
from services import spray_record_service, user_service, vineyard_service
from viewmodels.shared.viewmodel import ViewModelBase


class VineyardSprayRecordsEditSubmitViewModel(ViewModelBase):
    def __init__(
        self,
        vineyard_id: int,
        spray_record_id,
        operator_id: str,
        date_completed: datetime.datetime,
        growth_stage_id: int | None,
        hours_taken: Decimal | None,
        temperature: int | None,
        relative_humidity: int | None,
        wind_speed: int | None,
        wind_direction: str | None,
        management_unit_ids: list[int] | None,
        request: Request,
        session: Session,
    ):
        super().__init__(request, session)

        self.spray_record = spray_record_service.get_spray_record_by_id(
            session=self.session, id=spray_record_id
        )
        self.spray_record_id = spray_record_id
        self.vineyard_id = vineyard_id
        self.spray_id = self.spray_record.spray_id
        self.operator_id = operator_id
        self.date_completed = date_completed
        self.growth_stage_id = growth_stage_id
        self.hours_taken = hours_taken
        self.temperature = temperature
        self.relative_humidity = relative_humidity
        self.wind_speed = wind_speed
        self.wind_direction = wind_direction
        self.management_unit_ids = management_unit_ids
        self.form = {}
        self.wd_enum = None
        self.operator: User | None = user_service.get_user_by_id(
            self.session, self.operator_id
        )
        self.operators: List[User] = user_service.get_users_by_role(
            session=session, role=UserRole.OPERATOR
        )
        self.growth_stages = vineyard_service.all_growth_stages(session)
        self.chemicals = vineyard_service.get_spray_chemicals(self.spray_id, session)
        self.wind_directions = list(WindDirection)
        self.spray_records: list[SprayRecord] = (
            vineyard_service.eagerly_get_vineyard_spray_spray_records(
                self.session, self.vineyard_id, self.spray_id
            )
        )

    async def load(self):
        self.form = await self.request.form()

        if not self.operator_id:
            self.error = "An operator must be assigned to a completed"

        if not self.management_unit_ids:
            self.error = "At least one management unit must be selected."

        if self.wind_direction:
            try:
                self.wd_enum = WindDirection[self.wind_direction]
            except KeyError:
                self.error = f"Invalid wind direction: {self.wind_direction}"

        # Validate batch numbers
        program_chems = self.session.exec(
            select(SprayChemical)
            .order_by(SprayChemical.id)
            .where(SprayChemical.spray_id == self.spray_id)
        ).all()

        for pc in program_chems:
            key = f"batch_number_{pc.chemical_id}"
            if not self.form.get(key):
                self.error = f"Missing batch number for {pc.chemical.name}"
                return

    def process_submission(self):
        if self.error:
            return  # Do not proceed if there's an error

        # Fetch SprayChemicals
        program_chems = self.session.exec(
            select(SprayChemical).where(SprayChemical.spray_id == self.spray_id)
        ).all()

        # Map chemical_id -> batch_number
        chem_batch_map = {
            pc.chemical_id: self.form.get(f"batch_number_{pc.chemical_id}")
            for pc in program_chems
        }

        ic("##############################################################")
        ic(self.date_completed)
        ic("##############################################################")

        try:
            spray_record_service.update_multiple_spray_records(
                session=self.session,
                spray_id=self.spray_id,
                management_unit_ids=self.management_unit_ids,
                operator_id=self.operator_id,
                date_completed=self.date_completed,
                growth_stage_id=self.growth_stage_id,
                hours_taken=self.hours_taken,
                temperature=self.temperature,
                relative_humidity=self.relative_humidity,
                wind_speed=self.wind_speed,
                wind_direction=self.wd_enum,
                chem_batch_map=chem_batch_map,
            )
        except Exception as e:
            self.error = f"Failed to update spray records: {e}"
