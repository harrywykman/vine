from decimal import Decimal

from sqlmodel import Session
from starlette.requests import Request

from data.vineyard import Chemical
from services import vineyard_service
from viewmodels.shared.viewmodel import ViewModelBase


class CreateViewModel(ViewModelBase):
    def __init__(self, request: Request, session: Session):
        super().__init__(request, session)

        self.id: int = None
        self.name: str = None
        self.water_spray_rate_per_hectare: Decimal = None
        self.chemicals: list[Chemical] = []
        self.growth_stage_id: int = None
        self.chemical_ids: list = []
        self.targets: list = []

    async def load(self):
        form = await self.request.form()
        self.name = form.get("name")
        self.water_spray_rate_per_hectare = form.get("water_spray_rate_per_hectare")
        self.growth_stage_id = form.get("growth_stage_id")

        self.chemical_ids = form.getlist("chemical_ids")
        self.targets = form.getlist("targets")
        self.chemicals_targets = zip(self.chemical_ids, self.targets)

        self.growth_stages: list = vineyard_service.all_growth_stages(self.session)

        print("################## ZIP ################")
        print(self.chemicals_targets)
        print("################## ZIP ################")

        print("################## FORM ################")
        print(form)
        print("################## FORM ################")

        if not self.name or not self.name.strip():
            self.error = "A program name is required."
        elif not self.water_spray_rate_per_hectare:
            self.error = "A spray rate is required"
        elif len(self.chemical_ids) != len(self.targets):
            self.error = "Mismatch between chemicals and targets."
        # TODO check whether program with that name already in DB
