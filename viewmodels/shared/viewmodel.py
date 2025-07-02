from typing import Optional

from sqlalchemy.orm import Session
from starlette.requests import Request

from infrastructure import cookie_auth


class ViewModelBase:
    def __init__(self, request: Request, session: Session):
        self.request: Request = request
        self.session: Session = session
        self.error: Optional[str] = None
        self.info: Optional[str] = None
        self.user_id: Optional[int] = cookie_auth.get_user_id_via_auth_cookie(
            self.request
        )

        self.is_logged_in = self.user_id is not None

    # def to_dict(self) -> dict:
    #    return self.__dict__

    def to_dict(self) -> dict:
        return {
            key: value
            for key, value in self.__dict__.items()
            if key
            not in {
                "session",
                "request",
            }  # exclude non-serializable or recursive fields
        }
