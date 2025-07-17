from datetime import datetime

from sqlmodel import Session, select
from starlette.requests import Request

from data.vineyard import SprayProgram
from viewmodels.shared.viewmodel import ViewModelBase


class CreateViewModel(ViewModelBase):
    def __init__(self, request: Request, session: Session):
        super().__init__(request, session)

        self.id: int = None
        self.name: str = None
        self.year_start: int = datetime.now().year
        self.year_end: int = datetime.now().year + 1

    async def load(self):
        form = await self.request.form()
        self.name = form.get("name")
        self.year_start = form.get("year_start")
        self.year_end = form.get("year_end")

        print("################## FORM ################")
        print(form)
        print("################## FORM ################")

        if not self.name or not self.name.strip():
            self.error = "A program name is required."
        elif not self.year_start:
            self.error = "A year the spray program starts is required"
        elif not self.year_end:
            self.error = "A year the spray program ends is required. Can be the same as the Year Start."

        # Check for duplicate SprayProgram
        existing = self.session.exec(
            select(SprayProgram)
            .where(SprayProgram.name == self.name.strip())
            .where(SprayProgram.year_start == self.year_start)
            .where(SprayProgram.year_end == self.year_end)
        ).first()

        if existing:
            self.error = f"A spray program with the name '{self.name}' for years {self.year_start}-{self.year_end} already exists."
