from decimal import Decimal

from sqlmodel import Session
from starlette.requests import Request

from viewmodels.shared.viewmodel import ViewModelBase


class CreateViewModel(ViewModelBase):
    def __init__(self, request: Request, session: Session):
        super().__init__(request, session)

        self.id: int = None
        self.name: str = None
        self.water_spray_rate_per_hectare: Decimal = None
        self.chemicals: list[Chemical] = []
        self.chemicals_mix_rates = []

    async def load(self):
        form = await self.request.form()
        self.name = form.get("name")
        self.water_spray_rate_per_hectare = form.get("water_spray_rate_per_hectare")
        self.chemicals: list[Chemical] = []

        self.chemical_ids = form.getlist("chemical_ids")
        self.mix_rates = form.getlist("mix_rates")
        self.chemicals_mix_rates = zip(self.chemical_ids, self.mix_rates)

        print("################## ZIP ################")
        print(self.chemicals_mix_rates)
        print("################## ZIP ################")

        print("################## FORM ################")
        print(form)
        print("################## FORM ################")

        if not self.name or not self.name.strip():
            self.error = "A program name is required."
        elif not self.water_spray_rate_per_hectare:
            self.error = "A spray rate is required"
        elif len(self.chemical_ids) != len(self.mix_rates):
            self.error = "Mismatch between chemicals and rates."
        # TODO check whether program with that name already in DB
