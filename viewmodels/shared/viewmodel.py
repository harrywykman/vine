from typing import Optional

from icecream import ic
from sqlalchemy.orm import Session
from starlette.requests import Request

from data.user import User, UserRole
from infrastructure import cookie_auth

# from irrigation import irrigation_services
# from irrigation.models import IrrigationSeason
from services import spray_program_service
from services.user_service import get_user_by_id


class ViewModelBase:
    def __init__(self, request: Request, session: Session):
        self.request: Request = request
        self.session: Session = session
        self.error: Optional[str] = None
        self.info: Optional[str] = None
        self.success: Optional[str] = None
        self.warning: Optional[str] = None

        # Get user ID from cookie
        self.user_id: Optional[int] = cookie_auth.get_user_id_via_auth_cookie(
            self.request
        )
        self.is_logged_in = self.user_id is not None

        # Get full user object if logged in
        self.user: Optional[User] = None
        if self.user_id:
            self.user = get_user_by_id(self.session, self.user_id)
            # Double-check in case user was deleted but cookie still exists
            if not self.user:
                self.is_logged_in = False
                self.user_id = None

        # dict of booleans for modules (eg. irrigation / monitoring)
        self.modules = request.app.state.modules

        ic(self.modules)

        # --- Spray season context ---
        viewing_season_id = request.cookies.get("viewing_season_id")

        if viewing_season_id:
            self.current_season = spray_program_service.get_season_by_id(
                self.session, int(viewing_season_id)
            )
        else:
            self.current_season = spray_program_service.get_current_season(self.session)

        self.current_spray_programs = (
            self.current_season.spray_programs if self.current_season else []
        )
        self.current_spray_program_ids = {p.id for p in self.current_spray_programs}
        self.is_viewing_archive = bool(viewing_season_id)

    # Message helper methods

    def set_success(self, message: str):
        self.success = message

    def set_warning(self, message: str):
        self.warning = message

    def set_error(self, message: str):
        self.error = message

    def set_info(self, message: str):
        self.info = message

    # Permission helper methods
    def has_permission(self, required_role: UserRole) -> bool:
        """Check if current user has required permission level"""
        if not self.user:
            return False
        return self.user.has_permission(required_role)

    @property
    def is_admin(self) -> bool:
        """Check if current user is admin or higher"""
        if not self.user:
            return False
        return self.user.is_admin()

    @property
    def is_superadmin(self) -> bool:
        """Check if current user is superadmin"""
        if not self.user:
            return False
        return self.user.is_superadmin()

    @property
    def is_operator(self) -> bool:
        """Check if current user is operator or higher"""
        if not self.user:
            return False
        return self.user.has_permission(UserRole.OPERATOR)

    def require_permission(self, required_role: UserRole) -> None:
        """Raise exception if user doesn't have required permission"""
        if not self.has_permission(required_role):
            role_name = required_role.value if required_role else "authenticated user"
            raise PermissionError(f"Access denied. Required role: {role_name}")

    def require_login(self) -> None:
        """Raise exception if user is not logged in"""
        if not self.is_logged_in:
            raise PermissionError("Login required")

    def to_dict(self) -> dict:
        """Convert viewmodel to dictionary, excluding non-serializable fields"""
        result = {}
        for key, value in self.__dict__.items():
            if key not in {
                "session",
                "request",
            }:  # Exclude non-serializable fields
                result[key] = value

        # Add @properties to dict
        exposed_properties = ["is_superadmin", "is_admin", "is_operator"]
        for prop in exposed_properties:
            result[prop] = getattr(self, prop)

        return result
