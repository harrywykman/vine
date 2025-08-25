from fastapi import Request
from icecream import ic
from sqlmodel import Session

from services import user_service
from viewmodels.shared.viewmodel import ViewModelBase


class EditViewModel(ViewModelBase):
    def __init__(self, request: Request, session: Session):
        super().__init__(request, session)

        self.user_id = self.user.id

        ic(self.user_id)

        # Get the existing user
        self.existing_user = user_service.get_user_by_id(session, self.user_id)
        if not self.existing_user:
            self.error = "User not found"

        # Prevent users from editing themselves (optional - remove if you want to allow this)
        # if self.existing_user.id == self.user.id:
        #    self.error = "You cannot edit your own account"

        # Form data initialized with existing user data
        self.name: str = self.existing_user.name
        self.email: str = self.existing_user.email
        self.role: str = self.existing_user.role.value
        self.password: str = None  # Always start empty for security
        self.confirm_password: str = None
        self.success_message: str = ""

    async def load(self):
        form = await self.request.form()
        self.name = form.get("name")
        self.password = form.get("password")
        self.confirm_password = form.get("confirm_password")
        self.email = form.get("email")

        print("###########################################################")
        ic(self)
        ic(form)
        print("###########################################################")

        if not self.name or not self.name.strip():
            self.error = "Name is required."
        elif not self.email or not self.email.strip():
            self.error = "Email is required."
        elif self.password and len(self.password) < 8:
            self.error = "Password must be at least 8 characters if provided."
        elif self.password and not self.confirm_password:
            self.error = "Please confirm your password"
        elif self.password and self.password != self.confirm_password:
            self.error = "Passwords do not match"
        else:
            # Check if email is already taken by another user
            existing_user_with_email = user_service.get_user_by_email(
                self.session, self.email
            )
            if existing_user_with_email and existing_user_with_email.id != self.user_id:
                self.error = f"A user with email address {self.email} already exists. {self.existing_user.id} != {existing_user_with_email.id}?"
