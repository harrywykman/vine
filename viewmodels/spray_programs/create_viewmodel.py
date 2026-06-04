from sqlmodel import Session, select
from starlette.requests import Request

from data.vineyard import SprayProgram
from viewmodels.shared.viewmodel import ViewModelBase


class CreateViewModel(ViewModelBase):
    def __init__(self, request: Request, session: Session):
        super().__init__(request, session)

        self.id: int = None
        self.name: str = None

    async def load(self):
        form = await self.request.form()
        self.name = form.get("name")

        if not self.current_season:
            self.error = (
                "No current spray season is set. Please contact an administrator."
            )
            return

        if not self.name or not self.name.strip():
            self.error = "A program name is required."
            return

        existing = self.session.exec(
            select(SprayProgram)
            .where(SprayProgram.name == self.name.strip())
            .where(SprayProgram.spray_season_id == self.current_season.id)
        ).first()

        if existing:
            self.error = f"A spray program named '{self.name}' already exists for {self.current_season.name}."
