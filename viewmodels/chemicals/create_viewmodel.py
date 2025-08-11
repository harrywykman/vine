from typing import List, Optional

from fastapi import Request
from icecream import ic
from sqlmodel import Session, select

from data.user import UserRole
from data.vineyard import ChemicalGroup, MixRateUnit
from services import chemical_service
from viewmodels.shared.viewmodel import ViewModelBase


class CreateChemicalViewModel(ViewModelBase):
    def __init__(self, request: Request, session: Session):
        super().__init__(request, session)

        self.require_permission(UserRole.ADMIN)

        # Available mix rate units for the dropdown
        self.available_rate_units = [unit.value for unit in MixRateUnit]

        # Available chemical groups for checkboxes
        self.available_chemical_groups = session.exec(select(ChemicalGroup)).all()

        # Form data and validation errors
        self.name: str = ""
        self.active_ingredient: str = ""
        self.rate_per_100l: Optional[int] = None
        self.rate_unit: str = MixRateUnit.MILLILITRES.value
        self.chemical_group_ids: List[int] = []
        self.success_message: str = ""

    async def load(self):
        form = await self.request.form()
        self.name = form.get("name")
        self.active_ingredient = form.get("active_ingredient")
        self.rate_unit = form.get("rate_unit")

        # Handle rate_per_100l conversion
        rate_str = form.get("rate_per_100l")
        if rate_str:
            try:
                self.rate_per_100l = int(rate_str)
            except ValueError:
                self.rate_per_100l = None

        # Handle multiple chemical group selections
        self.chemical_group_ids = []
        for key in form.keys():
            if key.startswith("chemical_group_"):
                group_id = int(key.replace("chemical_group_", ""))
                self.chemical_group_ids.append(group_id)

        print("###########################################################")
        ic(self)
        ic(form)
        print("###########################################################")

        # Validation
        if not self.name or not self.name.strip():
            self.error = "Chemical name is required."
        elif not self.active_ingredient or not self.active_ingredient.strip():
            self.error = "Active ingredient is required."
        elif not self.rate_unit or not self.rate_unit.strip():
            self.error = "Rate unit is required."
        elif self.rate_per_100l is not None and self.rate_per_100l <= 0:
            self.error = "Rate per 100L must be a positive number if provided."
        elif chemical_service.get_chemical_by_name(self.session, self.name):
            self.error = f"A chemical with name '{self.name}' already exists."
