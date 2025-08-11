from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlmodel import or_, select
from starlette.requests import Request

from data.user import User, UserRole
from data.vineyard import Chemical, ChemicalGroup, SprayRecord, Vineyard
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
    def __init__(
        self,
        request: Request,
        session: Session,
        search: Optional[str] = None,
        role_filter: Optional[str] = None,
        success: str = "",
    ):
        super().__init__(request, session)

        # Ensure user has admin permissions
        self.require_permission(UserRole.ADMIN)

        # Build query with filters
        query = select(User).order_by(User.name)

        # Apply search filter
        if search and search.strip():
            search_term = f"%{search.strip()}%"
            query = query.where(
                or_(User.name.ilike(search_term), User.email.ilike(search_term))
            )

        # Apply role filter
        if role_filter and role_filter.strip():
            query = query.where(User.role == role_filter)

        # Load filtered users
        self.users: List[User] = session.exec(query).all()
        self.available_roles = [role.value for role in UserRole]

        # Current user can't promote to superadmin unless they are superadmin
        if not self.is_superadmin:
            self.available_roles = [
                role
                for role in self.available_roles
                if role != UserRole.SUPERADMIN.value
            ]

        # Store filter values for template
        self.search = search or ""
        self.role_filter = role_filter or ""

        if success:
            self.set_success(message=success)


class ChemicalManagementViewModel(ViewModelBase):
    def __init__(
        self,
        request: Request,
        session: Session,
        search: Optional[str] = None,
        group_filter: Optional[str] = None,
        success: str = "",
    ):
        super().__init__(request, session)

        self.require_permission(UserRole.ADMIN)

        self.search = search
        self.group_filter = group_filter
        self.success = success

        # Get all chemical groups for filter dropdown
        self.available_groups = session.exec(select(ChemicalGroup)).all()

        # Get filtered chemicals
        self.chemicals = self._get_filtered_chemicals()

    def _get_filtered_chemicals(self) -> List[Chemical]:
        """Get chemicals based on search and filter criteria"""
        query = select(Chemical)

        # Apply search filter
        if self.search and self.search.strip():
            search_term = f"%{self.search.strip()}%"
            query = query.where(
                or_(
                    Chemical.name.ilike(search_term),
                    Chemical.active_ingredient.ilike(search_term),
                )
            )

        # Apply group filter
        if self.group_filter and self.group_filter.strip():
            # Join with chemical groups through the many-to-many relationship
            query = query.join(Chemical.chemical_groups).where(
                ChemicalGroup.id == int(self.group_filter)
            )

        chemicals = self.session.exec(query).all()
        return sorted(chemicals, key=lambda x: x.name.lower())


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
