from typing import Dict, List, Optional

from sqlalchemy.orm import Session
from sqlmodel import select
from starlette.requests import Request

from data.user import UserRole
from data.vineyard import ManagementUnit, Spray, SprayProgram, SprayRecord
from viewmodels.shared.viewmodel import ViewModelBase


class MUSprayHistoryViewModel(ViewModelBase):
    def __init__(
        self,
        management_unit_id: int,
        request: Request,
        session: Session,
        spray_program_id: Optional[int] = None,
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

        # Get all spray programs for dropdown (ordered by most recent first)
        self.all_spray_programs: List[SprayProgram] = session.exec(
            select(SprayProgram).order_by(
                SprayProgram.year_start.desc(), SprayProgram.date_created.desc()
            )
        ).all()

        # Determine which spray program to use
        if spray_program_id:
            # Use specified spray program from query parameter
            selected_program = session.get(SprayProgram, spray_program_id)
            if not selected_program:
                # Fallback to most recent if specified program doesn't exist
                selected_program = (
                    self.all_spray_programs[0] if self.all_spray_programs else None
                )
        else:
            # Default to most recent spray program
            selected_program = (
                self.all_spray_programs[0] if self.all_spray_programs else None
            )

        self.selected_spray_program: Optional[SprayProgram] = selected_program

        # Get sprays for the selected program
        if selected_program:
            self.sprays: List[Spray] = session.exec(
                select(Spray)
                .where(Spray.spray_program_id == selected_program.id)
                .order_by(Spray.name)
            ).all()

            # Get spray records for this management unit and spray program
            spray_ids = [spray.id for spray in self.sprays]
            if spray_ids:
                self.spray_records: List[SprayRecord] = session.exec(
                    select(SprayRecord)
                    .where(
                        SprayRecord.management_unit_id == management_unit_id,
                        SprayRecord.spray_id.in_(spray_ids),
                    )
                    .order_by(
                        SprayRecord.date_completed.desc().nulls_last(),
                        SprayRecord.date_created.desc(),
                    )
                ).all()
            else:
                self.spray_records = []
        else:
            self.sprays = []
            self.spray_records = []

        # Create lookup dictionary for spray records by spray_id
        self.spray_record_lookup: Dict[int, SprayRecord] = {
            record.spray_id: record for record in self.spray_records
        }

        # Calculate completion statistics
        self.total_sprays = len(self.sprays)
        self.completed_sprays = len([r for r in self.spray_records if r.complete])
        self.pending_sprays = len(
            [r for r in self.spray_records if r.complete is False]
        )
        self.unassigned_sprays = self.total_sprays - len(self.spray_records)

        # Calculate completion percentage
        self.completion_percentage = int(
            (self.completed_sprays / self.total_sprays * 100)
            if self.total_sprays > 0
            else 0
        )
