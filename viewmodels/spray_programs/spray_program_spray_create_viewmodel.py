from decimal import Decimal

from sqlmodel import Session, select
from starlette.requests import Request

from data.vineyard import Chemical, Spray, SprayProgram
from services import spray_program_service, spray_service, vineyard_service
from viewmodels.shared.viewmodel import ViewModelBase


class CreateSprayProgramSprayViewModel(ViewModelBase):
    def __init__(self, request: Request, session: Session):
        super().__init__(request, session)
        self.id: int = None
        self.name: str = None
        self.water_spray_rate_per_hectare: Decimal = None
        self.chemicals: list[Chemical] = []
        self.growth_stage_id: int = None
        self.chemical_ids: list = []
        self.targets: list = []
        self.spray_program_id: int = None

    async def load(self):
        form = await self.request.form()
        self.name = form.get("name")
        self.water_spray_rate_per_hectare = form.get("water_spray_rate_per_hectare")
        self.growth_stage_id = form.get("growth_stage_id")
        self.chemical_ids = form.getlist("chemical_ids")
        self.targets = form.getlist("targets")
        self.chemicals_targets = zip(self.chemical_ids, self.targets)
        self.growth_stages: list = vineyard_service.all_growth_stages(self.session)
        self.spray_program_id: int = form.get("spray_program_id")
        self.spray_program: SprayProgram = (
            spray_program_service.get_spray_program_by_id(
                session=self.session, spray_program_id=self.spray_program_id
            )
        )

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
        else:
            # Check for existing spray with same name AND spray_program_id
            existing = self.session.exec(
                select(Spray).where(
                    Spray.name == self.name.strip(),
                    Spray.spray_program_id == self.spray_program_id,
                )
            ).first()

            if existing:
                self.error = f"A spray with the name '{self.name}' already exists in this program."

    def create_spray(self) -> Spray:
        spray = spray_service.create_spray(
            self.session,
            self.name,
            self.water_spray_rate_per_hectare,
            self.chemicals_targets,
            self.growth_stage_id,
            self.spray_program_id,
        )
        return spray
