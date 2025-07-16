from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlmodel import select
from starlette.requests import Request

from data.user import User, UserRole
from data.vineyard import SprayRecord, Vineyard
from services import spray_service, vineyard_service
from services.user_service import get_users_by_role
from viewmodels.shared.viewmodel import ViewModelBase


class AdminDashboardViewModel(ViewModelBase):
    def __init__(self, request: Request, session: Session):
        super().__init__(request, session)

        # Ensure user has admin permissions
        self.require_permission(UserRole.ADMIN)

        # Load admin dashboard data
        self.total_users = session.exec(select(func.count(User.id))).one()
        self.admin_users = get_users_by_role(session, UserRole.ADMIN)
        self.operator_users = get_users_by_role(session, UserRole.OPERATOR)
        self.regular_users = get_users_by_role(session, UserRole.USER)

        # User statistics
        self.user_stats = {
            "total": self.total_users,
            "admins": len(self.admin_users),
            "operators": len(self.operator_users),
            "regular": len(self.regular_users),
        }


class SprayProgressReportViewModel(ViewModelBase):
    def __init__(self, request: Request, session: Session):
        super().__init__(request, session)

        # Ensure user has admin permissions
        self.require_permission(UserRole.ADMIN)

        self.vineyards: List[Vineyard] = vineyard_service.all_vineyards(session)

        # self.vineyards = session.exec(select(Vineyard).order_by(Vineyard.name)).all()
        self.sprays = spray_service.eagerly_get_all_sprays(session)

        # Build lookup: {(management_unit_id, spray_id): SprayRecord}
        self.spray_records = session.exec(select(SprayRecord)).all()
        self.spray_lookup = {
            (rec.management_unit_id, rec.spray_id): rec for rec in self.spray_records
        }


class UserManagementViewModel(ViewModelBase):
    def __init__(self, request: Request, session: Session):
        super().__init__(request, session)

        # Ensure user has admin permissions
        self.require_permission(UserRole.ADMIN)

        # Load all users for management
        self.users: List[User] = session.exec(select(User)).all()
        self.available_roles = [role.value for role in UserRole]

        # Current user can't promote to superadmin unless they are superadmin
        if not self.is_superadmin():
            self.available_roles = [
                role
                for role in self.available_roles
                if role != UserRole.SUPERADMIN.value
            ]


class SystemAdminViewModel(ViewModelBase):
    def __init__(self, request: Request, session: Session):
        super().__init__(request, session)

        # Ensure user has superadmin permissions
        self.require_permission(UserRole.SUPERADMIN)

        # Load system admin data
        self.system_info = {
            "maintenance_mode": False,  # You'd load this from actual system state
            "total_users": session.exec(select(User)).count(),
            "database_size": "Unknown",  # You'd calculate this
            "last_backup": "Unknown",  # You'd load this from actual backup info
        }


class ReportsViewModel(ViewModelBase):
    def __init__(self, request: Request, session: Session):
        super().__init__(request, session)

        # Ensure user has operator permissions or higher
        self.require_permission(UserRole.OPERATOR)

        # Load report data
        self.user_activity = {
            "total_users": session.exec(select(User)).count(),
            "active_today": 0,  # You'd calculate from actual activity data
            "new_this_week": 0,  # You'd calculate from creation dates
            "login_this_week": 0,  # You'd calculate from login dates
        }

        # Role distribution
        self.role_distribution = {
            UserRole.SUPERADMIN.value: len(
                get_users_by_role(session, UserRole.SUPERADMIN)
            ),
            UserRole.ADMIN.value: len(get_users_by_role(session, UserRole.ADMIN)),
            UserRole.OPERATOR.value: len(get_users_by_role(session, UserRole.OPERATOR)),
            UserRole.USER.value: len(get_users_by_role(session, UserRole.USER)),
        }
