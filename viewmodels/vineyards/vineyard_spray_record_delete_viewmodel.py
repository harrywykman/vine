from typing import Optional

from sqlmodel import Session
from starlette.requests import Request

from data.vineyard import ManagementUnit, Spray, SprayRecord, Vineyard
from services import spray_record_service, vineyard_service
from viewmodels.shared.viewmodel import ViewModelBase


class VineyardSprayRecordDelete(ViewModelBase):
    def __init__(
        self, vineyard_id: int, spray_record_id: int, request: Request, session: Session
    ):
        super().__init__(request, session)

        self.id: int = vineyard_id
        self.name: Optional[str] = None
        self.address: Optional[str] = None
        self.spray_record_id: int = spray_record_id
        self.vineyard: Vineyard = vineyard_service.get_vineyard_by_id(
            self.session, vineyard_id
        )

        if spray_record_id:
            try:
                spray_record_service.delete_spray_record_by_id(
                    session=session, id=spray_record_id
                )
                self.success = "Successfully deleted incomplete spray record."
            except Exception as e:
                self.session.rollback()
                self.set_error(f"Error deleting spray_record: {str(e)}")
                return
        else:
            self.set_error("No spray record id given")
            return

        self.management_units: Optional(List[ManagementUnit]) = (
            vineyard_service.eagerly_get_vineyard_managment_units_by_id(
                self.session, self.id
            )
        )

        self.sprays: list[Spray] = vineyard_service.eagerly_get_vineyard_sprays(
            self.session, self.id
        )

        self.spray_records: list[SprayRecord] = (
            vineyard_service.eagerly_get_vineyard_spray_records(self.session, self.id)
        )

        # Add spray program completion status as a dictionary
        # This creates a mapping of spray_id -> completion_status
        self.spray_completion_status: dict[int, bool] = {}

        # Add spray program completion dates as a dictionary
        # This creates a mapping of spray_id -> formatted_completion_date
        self.spray_completion_dates: dict[int, str] = {}

        for spray in self.sprays:
            self.spray_completion_status[spray.id] = (
                vineyard_service.spray_complete_for_vineyard(
                    self.session, spray.id, self.id
                )
            )

            # Get most recent completion date for this spray program
            completed_records = [
                record
                for record in self.spray_records
                if (record.spray_id == spray.id and record.date_completed is not None)
            ]

            if completed_records:
                # Find the most recent completion date
                most_recent_record = max(
                    completed_records, key=lambda x: x.date_completed
                )
                self.spray_completion_dates[spray.id] = (
                    most_recent_record.date_completed.strftime("%d/%m/%Y")
                )
            else:
                self.spray_completion_dates[spray.id] = None
