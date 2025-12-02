from collections import defaultdict
from typing import Dict, List, Optional

from sqlalchemy.orm import Session
from sqlmodel import select
from starlette.requests import Request

from data.user import UserRole
from data.vineyard import ManagementUnit, Spray, SprayProgram, SprayRecord, Vineyard
from viewmodels.shared.viewmodel import ViewModelBase


class VineyardFullSprayHistoryViewModel(ViewModelBase):
    def __init__(
        self,
        vineyard_id: int,
        request: Request,
        session: Session,
    ):
        super().__init__(request, session)

        # Require at least operator permissions to view spray history
        self.require_permission(UserRole.OPERATOR)

        # Get the vineyard
        self.vineyard: Optional[Vineyard] = session.get(Vineyard, vineyard_id)
        if not self.vineyard:
            raise ValueError(f"Vineyard with ID {vineyard_id} not found")

        # Get all management units for this vineyard
        management_unit_ids = [mu.id for mu in self.vineyard.management_units]

        if management_unit_ids:
            # Get all spray records for all management units in this vineyard
            self.spray_records: List[SprayRecord] = session.exec(
                select(SprayRecord)
                .where(SprayRecord.management_unit_id.in_(management_unit_ids))
                .order_by(
                    SprayRecord.date_completed.desc().nulls_last(),
                    SprayRecord.date_created.desc(),
                )
            ).all()

            # Get associated sprays and programs for the records
            spray_ids = [record.spray_id for record in self.spray_records]
            if spray_ids:
                self.sprays: List[Spray] = session.exec(
                    select(Spray).where(Spray.id.in_(spray_ids))
                ).all()

                program_ids = list(set(spray.spray_program_id for spray in self.sprays))
                self.spray_programs: List[SprayProgram] = session.exec(
                    select(SprayProgram)
                    .where(SprayProgram.id.in_(program_ids))
                    .order_by(
                        SprayProgram.year_start.desc(), SprayProgram.date_created.desc()
                    )
                ).all()
            else:
                self.sprays = []
                self.spray_programs = []

            # Get management units that have records
            mu_ids_with_records = list(
                set(record.management_unit_id for record in self.spray_records)
            )
            self.management_units: List[ManagementUnit] = session.exec(
                select(ManagementUnit).where(ManagementUnit.id.in_(mu_ids_with_records))
            ).all()
        else:
            self.spray_records = []
            self.sprays = []
            self.spray_programs = []
            self.management_units = []

        # Create lookup dictionaries for efficient access
        self.spray_lookup = {spray.id: spray for spray in self.sprays}
        self.program_lookup = {program.id: program for program in self.spray_programs}
        self.management_unit_lookup = {mu.id: mu for mu in self.management_units}

        # Group records by program, then by management unit
        # Structure: {program_id: {mu_id: [records]}}
        self.records_by_program_and_mu: Dict[int, Dict[int, List[SprayRecord]]] = (
            defaultdict(lambda: defaultdict(list))
        )
        for record in self.spray_records:
            spray = self.spray_lookup.get(record.spray_id)
            if spray:
                self.records_by_program_and_mu[spray.spray_program_id][
                    record.management_unit_id
                ].append(record)

        # Create a sorted list of management unit IDs for each program
        # Sorted by management unit name
        self.sorted_mu_ids_by_program: Dict[int, List[int]] = {}
        for program_id, mu_dict in self.records_by_program_and_mu.items():
            # Sort MU IDs by the name of the management unit
            sorted_ids = sorted(
                mu_dict.keys(),
                key=lambda mu_id: self.management_unit_lookup.get(mu_id).name
                if self.management_unit_lookup.get(mu_id)
                else "",
            )
            self.sorted_mu_ids_by_program[program_id] = sorted_ids

        # Calculate statistics
        self.total_records = len(self.spray_records)
        self.completed_records = len([r for r in self.spray_records if r.complete])
        self.pending_records = len(
            [r for r in self.spray_records if r.complete is False]
        )

        # Calculate completion percentage
        self.completion_percentage = int(
            (self.completed_records / self.total_records * 100)
            if self.total_records > 0
            else 0
        )
