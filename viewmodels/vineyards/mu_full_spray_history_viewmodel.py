from collections import defaultdict
from typing import Dict, List, Optional

from sqlalchemy.orm import Session
from sqlmodel import select
from starlette.requests import Request

from data.user import UserRole
from data.vineyard import ManagementUnit, Spray, SprayProgram, SprayRecord
from viewmodels.shared.viewmodel import ViewModelBase


class MUFullSprayHistoryViewModel(ViewModelBase):
    def __init__(
        self,
        management_unit_id: int,
        request: Request,
        session: Session,
    ):
        super().__init__(request, session)

        # Require at least operator permissions to view spray history
        self.require_permission(UserRole.OPERATOR)

        # Get the management unit
        self.management_unit: Optional[ManagementUnit] = session.get(
            ManagementUnit, management_unit_id
        )
        if not self.management_unit:
            raise ValueError(f"Management Unit with ID {management_unit_id} not found")

        # Get all spray records for this management unit, ordered by most recent first
        self.spray_records: List[SprayRecord] = session.exec(
            select(SprayRecord)
            .where(SprayRecord.management_unit_id == management_unit_id)
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

        # Create lookup dictionaries for efficient access
        self.spray_lookup = {spray.id: spray for spray in self.sprays}
        self.program_lookup = {program.id: program for program in self.spray_programs}

        # Group records by program (maintaining chronological order within each program)
        self.records_by_program: Dict[int, List[SprayRecord]] = defaultdict(list)
        for record in self.spray_records:
            spray = self.spray_lookup.get(record.spray_id)
            if spray:
                self.records_by_program[spray.spray_program_id].append(record)

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
