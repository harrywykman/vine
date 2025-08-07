"""
Admin-only routes for user management, system administration, etc.
"""

import fastapi_chameleon
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select

from auth.permissions_decorators import (
    require_admin,
    require_admin_user,
    require_superadmin,
    require_superadmin_user,
)
from data.user import User, UserRole
from dependencies import get_current_user, get_session
from services.user_service import get_users_by_role, update_user_role
from viewmodels.admin.admin_viewmodels import (
    AdminDashboardViewModel,
    SprayProgressReportViewModel,
    UserManagementViewModel,
)

router = APIRouter(prefix="/administration", tags=["admin"])


@router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
@require_admin()
@fastapi_chameleon.template("admin/dashboard.pt")
async def admin_dashboard(request: Request, session: Session = Depends(get_session)):
    """Admin dashboard - accessible to admins and superadmins"""
    try:
        vm = AdminDashboardViewModel(request, session)
        return vm.to_dict()
    except PermissionError as e:
        if "Login required" in str(e):
            return RedirectResponse(url="/login", status_code=302)
        else:
            return RedirectResponse(url="/unauthorised", status_code=302)


@router.get(
    "/reports/spray_progress", response_class=HTMLResponse, include_in_schema=False
)
@require_admin()
@fastapi_chameleon.template("admin/spray_progress.pt")
async def spray_progress_report(
    request: Request, session: Session = Depends(get_session)
):
    vm = SprayProgressReportViewModel(request, session)

    return vm.to_dict()


## Example routes from Claude


@router.get("/users", response_class=HTMLResponse, include_in_schema=False)
@require_admin()
async def manage_users(request: Request, session: Session = Depends(get_session)):
    """User management page - accessible to admins and superadmins"""
    try:
        vm = UserManagementViewModel(request, session)
        return templates.TemplateResponse("admin/users.html", vm.to_dict())
    except PermissionError as e:
        if "Login required" in str(e):
            return RedirectResponse(url="/account/login", status_code=302)
        else:
            return RedirectResponse(url="/unauthorised", status_code=302)


@router.post("/users/{user_id}/role", include_in_schema=False)
@require_admin()
async def change_user_role(
    user_id: int,
    new_role: UserRole,
    current_user: User = Depends(require_admin_user()),
    session: Session = Depends(get_session),
):
    """Change user role - admin API endpoint"""
    try:
        updated_user = update_user_role(session, user_id, new_role, current_user)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "message": "Role updated successfully",
            "user_id": user_id,
            "new_role": new_role.value,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/reports", response_class=HTMLResponse, include_in_schema=False)
@require_admin()
async def admin_reports(
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Admin reports page"""
    # Get user statistics
    user_stats = {
        "total_users": session.exec(select(User)).count(),
        "admins": len(get_users_by_role(session, UserRole.ADMIN)),
        "operators": len(get_users_by_role(session, UserRole.OPERATOR)),
        "regular_users": len(get_users_by_role(session, UserRole.USER)),
    }

    return templates.TemplateResponse(
        "admin/reports.html",
        {"request": request, "current_user": current_user, "user_stats": user_stats},
    )


# Superadmin-only routes
@router.get("/system", response_class=HTMLResponse, include_in_schema=False)
@require_superadmin()
async def system_admin(
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """System administration - superadmin only"""
    return templates.TemplateResponse(
        "admin/system.html", {"request": request, "current_user": current_user}
    )


@router.delete("/users/{user_id}", include_in_schema=False)
@require_admin()
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_superadmin_user()),
    session: Session = Depends(get_session),
):
    """Delete user - superadmin only"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    session.delete(user)
    session.commit()
    return {"message": "User deleted successfully"}
