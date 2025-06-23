from typing import Optional

from sqlmodel import Session
from starlette.requests import Request

from data.user import User
from services import user_service
from viewmodels.shared.viewmodel import ViewModelBase


class AccountViewModel(ViewModelBase):
    def __init__(self, request: Request, session: Session):
        super().__init__(request, session)
        self.user: Optional[User] = user_service.get_user_by_id(
            self.session, self.user_id
        )

    def load(self):
        self.user = user_service.get_user_by_id(self.session, self.user_id)
        print(f"Loaded {self.user.name}")
