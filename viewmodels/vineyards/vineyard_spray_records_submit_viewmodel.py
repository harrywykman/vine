import datetime
from decimal import Decimal
from typing import List

from fastapi import Request
from sqlmodel import Session, select

from data.user import User, UserRole
from data.vineyard import (
    SprayChemical,
    SprayRecord,
    SprayRecordChemical,
    WindDirection,
)
from services import user_service, vineyard_service
from viewmodels.shared.viewmodel import ViewModelBase


class VineyardSprayRecordsSubmitViewModel(ViewModelBase):
    def __init__(
        self,
        vineyard_id: int,
        spray_id: int,
        operator_id: str,
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

        self.vineyard_id = vineyard_id
        self.spray_id = spray_id
        self.operator_id = operator_id
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
            self.session, self.user_id
        )
        self.operators: List[User] = user_service.get_users_by_role(
            session=session, role=UserRole.OPERATOR
        )
        self.growth_stages = vineyard_service.all_growth_stages(session)
        self.chemicals = vineyard_service.get_spray_chemicals(spray_id, session)
        self.wind_directions = list(WindDirection)
        self.spray_records: list[SprayRecord] = (
            vineyard_service.eagerly_get_vineyard_spray_spray_records(
                self.session, self.vineyard_id, spray_id
            )
        )

    async def load(self):
        self.form = await self.request.form()

        if not self.operator_id:
            self.error = "An operator must be assigned to a completed"

        if not self.management_unit_ids:
            self.error = "At least one management unit must be selected."

        if self.management_unit_ids:
            self.error = f"Alt case - {self.management_unit_ids}At least one management unit must be selected."

        if self.wind_direction:
            try:
                self.wd_enum = WindDirection[self.wind_direction]
            except KeyError:
                self.error = f"Invalid wind direction: {self.wind_direction}"

        # Validate batch numbers
        program_chems = self.session.exec(
            select(SprayChemical).where(SprayChemical.spray_id == self.spray_id)
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

        for mu_id in self.management_unit_ids:
            spray_record = self.session.exec(
                select(SprayRecord).where(
                    SprayRecord.management_unit_id == int(mu_id),
                    SprayRecord.spray_id == self.spray_id,
                )
            ).first()

            if not spray_record:
                continue

            spray_record.operator_id = self.operator_id
            spray_record.growth_stage_id = self.growth_stage_id
            spray_record.hours_taken = self.hours_taken
            spray_record.temperature = self.temperature
            spray_record.relative_humidity = self.relative_humidity
            spray_record.wind_speed = self.wind_speed
            spray_record.wind_direction = self.wd_enum
            spray_record.complete = True
            spray_record.date_completed = datetime.datetime.now()

            for chem_id, batch_number in chem_batch_map.items():
                # Ensure no duplicates added
                existing: SprayRecordChemical = self.session.exec(
                    select(SprayRecordChemical).where(
                        SprayRecordChemical.spray_record_id == spray_record.id,
                        SprayRecordChemical.chemical_id == chem_id,
                    )
                ).first()

                if existing:
                    existing.batch_number = batch_number
                    src = existing
                else:
                    src = SprayRecordChemical(
                        spray_record_id=spray_record.id,
                        chemical_id=chem_id,
                        batch_number=batch_number,
                    )

                self.session.add(src)

            self.session.add(spray_record)

        self.session.commit()
