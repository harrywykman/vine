from fastapi import Request
from sqlmodel import Session

from services import spray_record_service, spray_service, vineyard_service
from viewmodels.shared.viewmodel import ViewModelBase


class ApplySelectUnitsSubmitViewModel(ViewModelBase):
    def __init__(
        self,
        spray_id: int,
        management_unit_ids: list[int],
        request: Request,
        session: Session,
    ):
        super().__init__(request, session)

        self.spray_id = spray_id
        self.management_unit_ids = management_unit_ids
        self.form = {}
        self.spray = spray_service.eagerly_get_spray_by_id(spray_id, session)
        self.vineyards = vineyard_service.all_vineyards_with_mangement_units(
            session=session
        )

    async def load(self):
        self.form = await self.request.form()

        if not self.management_unit_ids:
            self.error = "At least one management unit must be selected."
            return

    def process_submission(self):
        added_units = "<ul>"

        for mu_id in self.management_unit_ids:
            mu = vineyard_service.eagerly_get_management_unit_by_id(
                session=self.session, id=mu_id
            )
            if mu.is_active:
                spray_record = spray_record_service.create_or_update_spray_record(
                    self.session, mu.id, self.spray_id
                )
                self.session.add(spray_record)
                print(
                    f"################## Added {mu.vineyard.name} {mu.name_with_variety} ###################"
                )
                added_units += f"<li> {mu.vineyard.name} - {mu.name_with_variety} </li>"
            else:
                print(f"################## Skipped {mu.name} ###################")

        self.session.commit()

        spray = spray_service.eagerly_get_spray_by_id(
            id=self.spray_id, session=self.session
        )

        self.success = (
            f"Successfully added {spray.name} to selected management units: <br/>"
        )
        self.success += f"{added_units} </ul>"
