import datetime
from enum import Enum
from typing import List

import sqlalchemy as sa
from sqlmodel import Field, Relationship, SQLModel


class UserRole(str, Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    OPERATOR = "operator"
    USER = "user"  # Default role for regular users


class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore

    id: int = Field(default=None, primary_key=True)
    name: str = Field(default=None)
    email: str = Field(index=True, unique=True)
    hash_password: str = Field()
    role: UserRole = Field(default=UserRole.USER)  # Default to regular user
    created_date: datetime.datetime = Field(
        sa_column=sa.Column(sa.DateTime, default=datetime.datetime.now, index=True)
    )
    last_login: datetime.datetime = Field(
        sa_column=sa.Column(sa.DateTime, default=datetime.datetime.now, index=True)
    )

    spray_records: List["SprayRecord"] | None = Relationship(back_populates="operator")  # noqa: F821

    def has_permission(self, required_role: UserRole) -> bool:
        """Check if user has required permission level"""
        role_hierarchy = {
            UserRole.USER: 0,
            UserRole.OPERATOR: 1,
            UserRole.ADMIN: 2,
            UserRole.SUPERADMIN: 3,
        }
        return role_hierarchy.get(self.role, 0) >= role_hierarchy.get(required_role, 0)

    def is_admin(self) -> bool:
        """Check if user is admin or higher"""
        return self.has_permission(UserRole.ADMIN)

    def is_superadmin(self) -> bool:
        """Check if user is superadmin"""
        return self.role == UserRole.SUPERADMIN


# Uncomment when running import modules - Define the relationship after both classes are available
# User.spray_records = Relationship(back_populates="operator")
