import datetime
from typing import Optional

from sqlmodel import Session
from starlette.requests import Request

from viewmodels.shared.viewmodel import ViewModelBase


class ArchiveSeasonViewModel(ViewModelBase):
    def __init__(self, request: Request, session: Session):
        super().__init__(request, session)

        self.new_season_name: Optional[str] = None
        self.new_season_start: Optional[datetime.date] = None
        self.new_season_end: Optional[datetime.date] = None

    async def load(self):
        form = await self.request.form()
        self.new_season_name = form.get("new_season_name")

        raw_start = form.get("new_season_start")
        raw_end = form.get("new_season_end")

        self.new_season_start = (
            datetime.date.fromisoformat(raw_start) if raw_start else None
        )
        self.new_season_end = datetime.date.fromisoformat(raw_end) if raw_end else None

        if not self.current_season:
            self.error = "No current season found to archive."
            return

        if not self.new_season_name or not self.new_season_name.strip():
            self.error = "A name for the new season is required."
            return

        if not self.new_season_start or not self.new_season_end:
            self.error = "A start and end date for the new season are required."
            return

        if self.new_season_end <= self.new_season_start:
            self.error = "Season end date must be after start date."
            return
