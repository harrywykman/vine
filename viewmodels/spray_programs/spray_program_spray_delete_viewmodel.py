from sqlmodel import Session
from starlette.requests import Request

from data.vineyard import Spray, SprayProgram
from services import spray_program_service, spray_service
from viewmodels.shared.viewmodel import ViewModelBase


class SprayDeleteViewModel(ViewModelBase):
    def __init__(
        self,
        request: Request,
        session: Session,
        spray_program_id: int,
        spray_id: int,
    ):
        super().__init__(request, session)

        self.spray_program: SprayProgram = (
            spray_program_service.get_spray_program_by_id(
                session=session, spray_program_id=spray_program_id
            )
        )
        if not self.spray_program:
            self.set_error("Spray program not found")
            return

        self.sprays: list[Spray] = (
            spray_program_service.eagerly_get_all_spray_program_sprays(
                session=session, spray_program_id=self.spray_program.id
            )
        )

        self.spray = spray_service.eagerly_get_spray_by_id(
            session=self.session, id=spray_id
        )
        if not self.spray:
            self.set_error("Spray not found")
            return

    def delete_spray(self):
        if self.spray.has_completed_spray_records:
            self.set_error(
                f"Cannot delete {self.spray.name} as it has completed spray records associated with it."
            )
            return
        else:
            spray_service.delete_spray(self.session, self.spray.id)

            self.set_success(
                message=f"Deleted {self.spray.name} from {self.spray_program.name}"
            )
            self.sprays: list[Spray] = (
                spray_program_service.eagerly_get_all_spray_program_sprays(
                    session=self.session, spray_program_id=self.spray_program.id
                )
            )
            return
