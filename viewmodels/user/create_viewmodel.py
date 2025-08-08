from fastapi.requests import Request
from icecream import ic
from sqlmodel import Session

from data.user import UserRole
from services import user_service
from viewmodels.shared.viewmodel import ViewModelBase


class CreateUserViewModel(ViewModelBase):
    def __init__(self, request: Request, session: Session):
        super().__init__(request, session)

        self.require_permission(UserRole.ADMIN)

        # Available roles for the dropdown
        self.available_roles = [role.value for role in UserRole]

        # Current user can't assign superadmin unless they are superadmin
        if not self.is_superadmin:
            self.available_roles = [
                role
                for role in self.available_roles
                if role != UserRole.SUPERADMIN.value
            ]

        # Form data and validation errors
        self.name: str = ""
        self.email: str = ""
        self.role: str = UserRole.USER.value
        self.password: str = None
        self.confirm_password: str = None
        self.success_message: str = ""

    async def load(self):
        form = await self.request.form()
        self.name = form.get("name")
        self.password = form.get("password")
        self.confirm_password = form.get("confirm_password")
        self.email = form.get("email")
        self.role = form.get("role")

        print("###########################################################")
        ic(self)
        ic(form)
        print("###########################################################")

        if not self.name or not self.name.strip():
            self.error = "Your name is required."
        elif not self.email or not self.email.strip():
            self.error = "Your email is required."
        elif not self.role or not self.role.strip():
            self.error = "A role is required."
        elif not self.password or len(self.password) < 8:
            self.error = "Your password is required and must be at 8 characters."
        elif not self.confirm_password:
            self.error = "Please confirm your password"
        elif self.password != self.confirm_password:
            self.error = "Passwords do not match"
        elif self.role == UserRole.SUPERADMIN and not self.is_superadmin:
            self.error = "You don't have permission to assign superadmin role"
        elif user_service.get_user_by_email(self.session, self.email):
            self.error = f"A user with email addess {self.email} already exists."
