"""
Admin-only routes for user management, system administration, etc.
"""

from typing import Optional
from urllib.parse import urlencode

import fastapi_chameleon
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from icecream import ic
from sqlmodel import Session, select

from auth.permissions_decorators import (
    require_admin,
    require_superadmin,
    require_superadmin_user,
)
from data.user import User, UserRole
from dependencies import get_current_user, get_session
from services import chemical_service, user_service
from services.user_service import get_users_by_role
from viewmodels.admin.admin_viewmodels import (
    AdminDashboardViewModel,
    ChemicalManagementViewModel,
    SprayProgressReportViewModel,
    UserManagementViewModel,
)
from viewmodels.chemicals.create_viewmodel import CreateChemicalViewModel
from viewmodels.chemicals.edit_viewmodel import EditChemicalViewModel
from viewmodels.user.create_viewmodel import CreateUserViewModel
from viewmodels.user.edit_viewmodel import EditUserViewModel

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
    request: Request,
    session: Session = Depends(get_session),
    spray_program_id: Optional[int] = None,
):
    vm = SprayProgressReportViewModel(request, session, spray_program_id)
    return vm.to_dict()


## Example routes from Claude


@router.get("/users", response_class=HTMLResponse, include_in_schema=False)
@fastapi_chameleon.template("admin/users.pt")
@require_admin()
async def manage_users(
    request: Request,
    session: Session = Depends(get_session),
    search: Optional[str] = None,
    role_filter: Optional[str] = None,
    success: str = "",
):
    """User management page - accessible to admins and superadmins"""
    try:
        vm = UserManagementViewModel(
            request, session, search, role_filter, success=success
        )
        return vm.to_dict()
    except PermissionError as e:
        if "Login required" in str(e):
            return RedirectResponse(url="/account/login", status_code=302)
        else:
            return RedirectResponse(url="/unauthorised", status_code=302)


@router.get("/users/table", response_class=HTMLResponse, include_in_schema=False)
@fastapi_chameleon.template("admin/_users_table.pt")
@require_admin()
async def users_table_htmx(
    request: Request,
    session: Session = Depends(get_session),
    search: Optional[str] = None,
    role_filter: Optional[str] = None,
):
    """HTMX endpoint for user table content"""
    try:
        vm = UserManagementViewModel(request, session, search, role_filter)
        return vm.to_dict()
    except PermissionError as e:
        if "Login required" in str(e):
            return RedirectResponse(url="/account/login", status_code=302)
        else:
            return RedirectResponse(url="/unauthorised", status_code=302)


@router.get("/users/new")
@require_admin()
@fastapi_chameleon.template("admin/user_form.pt")
async def users_new_get(request: Request, session: Session = Depends(get_session)):
    """Display form for creating a new user"""
    vm = CreateUserViewModel(request, session)

    if not vm:
        raise HTTPException(status_code=404, detail="No view model.")
    if vm.error:
        print(vm.error)
        return vm.to_dict()
    return vm.to_dict()


@router.post("/users/new")
@require_admin()
@fastapi_chameleon.template("admin/user_form.pt")
async def users_new_post(
    request: Request,
    session: Session = Depends(get_session),
):
    vm = CreateUserViewModel(request, session)

    if not vm:
        raise HTTPException(status_code=404, detail="No view model.")

    await vm.load()

    if vm.error:
        print(vm.error)
        return vm.to_dict()

    ic(vm)
    ic(vm.password)

    user = user_service.create_user(
        session=session,
        name=vm.name,
        email=vm.email,
        password=vm.password,
        role=vm.role,
    )

    if user:
        # Redirect back to user management with success message
        params = urlencode({"success": "User created successfully"})
        response = RedirectResponse(
            url=f"/administration/users?{params}",
            status_code=303,
        )
        response.headers["HX-Push-Url"] = "/administration/users"
        return response

    # Return form with errors
    return vm.to_dict()


@router.get("/users/{user_id}/edit")
@require_admin()
@fastapi_chameleon.template("admin/edit_user_form.pt")
async def users_edit_get(
    request: Request, user_id: int, session: Session = Depends(get_session)
):
    """Display form for editing an existing user"""
    vm = EditUserViewModel(request, session, user_id)
    ic(vm)
    if not vm:
        raise HTTPException(status_code=404, detail="No view model.")
    if vm.error:
        print(vm.error)
        return vm.to_dict()
    return vm.to_dict()


@router.post("/users/{user_id}/edit")
@require_admin()
@fastapi_chameleon.template("admin/edit_user_form.pt")
async def users_edit_post(
    request: Request,
    user_id: int,
    session: Session = Depends(get_session),
):
    vm = EditUserViewModel(request, session, user_id)

    if not vm:
        raise HTTPException(status_code=404, detail="No view model.")

    await vm.load()

    if vm.error:
        print(vm.error)
        return vm.to_dict()

    ic(vm)

    # Update the user
    updated_user = user_service.update_user(
        session=session,
        user_id=user_id,
        name=vm.name,
        email=vm.email,
        role=vm.role,
        password=vm.password
        if vm.password
        else None,  # Only update password if provided
    )

    if updated_user:
        # Redirect back to user management with success message
        params = urlencode({"success": "User updated successfully"})
        response = RedirectResponse(
            url=f"/administration/users?{params}",
            status_code=303,
        )
        response.headers["HX-Push-Url"] = "/administration/users"
        return response

    # Return form with errors
    vm.error = "Failed to update user"
    return vm.to_dict()


@router.delete("/users/{user_id}")
@require_admin()
@fastapi_chameleon.template("admin/users.pt")
async def users_delete(
    request: Request,
    user_id: int,
    session: Session = Depends(get_session),
):
    """Delete a user"""
    vm = UserManagementViewModel(
        request, session
    )  # Assuming you have this for the main users page

    if not vm:
        raise HTTPException(status_code=404, detail="No view model.")

    # Get the user to delete
    user_to_delete = user_service.get_user_by_id(session, user_id)
    if not user_to_delete:
        vm.error = "User not found"
        return vm.to_dict()

    # Security checks
    if user_to_delete.id == vm.user.id:
        vm.error = "You cannot delete your own account"
        return vm.to_dict()

    if user_to_delete.role == UserRole.SUPERADMIN and not vm.is_superadmin:
        vm.error = "You don't have permission to delete superadmin users"
        return vm.to_dict()

    if user_to_delete.has_spray_records:
        vm.error = f"User {user_to_delete.name} cannot be deleted because there are spray records associated. Make user inactive instead."
        return vm.to_dict()

    # Attempt to delete the user
    try:
        deleted = user_service.delete_user(session, user_id)
        if not deleted:
            vm.error = "Failed to delete user"
    except Exception as e:
        print(f"Error deleting user: {e}")
        vm.error = "An error occurred while deleting the user"

    vm = UserManagementViewModel(
        request, session
    )  # Assuming you have this for the main users page

    if not vm:
        raise HTTPException(status_code=404, detail="No view model.")

    vm.set_success(
        message=f"User '{user_to_delete.name}' has been deleted successfully"
    )

    return vm.to_dict()


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


################## CHEMICAL MANAGEMENT ROUTES ###############################


@router.get("/chemicals", response_class=HTMLResponse, include_in_schema=False)
@fastapi_chameleon.template("admin/chemicals.pt")
@require_admin()
async def manage_chemicals(
    request: Request,
    session: Session = Depends(get_session),
    search: Optional[str] = None,
    group_filter: Optional[str] = None,
    success: str = "",
):
    """Chemical management page - accessible to admins and superadmins"""
    try:
        vm = ChemicalManagementViewModel(
            request, session, search, group_filter, success=success
        )
        return vm.to_dict()
    except PermissionError as e:
        if "Login required" in str(e):
            return RedirectResponse(url="/account/login", status_code=302)
        else:
            return RedirectResponse(url="/unauthorised", status_code=302)


@router.get("/chemicals/table", response_class=HTMLResponse, include_in_schema=False)
@fastapi_chameleon.template("admin/_chemicals_table.pt")
@require_admin()
async def chemicals_table_htmx(
    request: Request,
    session: Session = Depends(get_session),
    search: Optional[str] = None,
    group_filter: Optional[str] = None,
):
    """HTMX endpoint for chemical table content"""
    try:
        vm = ChemicalManagementViewModel(request, session, search, group_filter)
        return vm.to_dict()
    except PermissionError as e:
        if "Login required" in str(e):
            return RedirectResponse(url="/account/login", status_code=302)
        else:
            return RedirectResponse(url="/unauthorised", status_code=302)


@router.get("/chemicals/new")
@require_admin()
@fastapi_chameleon.template("admin/chemical_form.pt")
async def chemicals_new_get(request: Request, session: Session = Depends(get_session)):
    """Display form for creating a new chemical"""
    vm = CreateChemicalViewModel(request, session)

    if not vm:
        raise HTTPException(status_code=404, detail="No view model.")
    if vm.error:
        print(vm.error)
        return vm.to_dict()
    return vm.to_dict()


@router.post("/chemicals/new")
@require_admin()
@fastapi_chameleon.template("admin/chemical_form.pt")
async def chemicals_new_post(
    request: Request,
    session: Session = Depends(get_session),
):
    vm = CreateChemicalViewModel(request, session)

    if not vm:
        raise HTTPException(status_code=404, detail="No view model.")

    await vm.load()

    if vm.error:
        print(vm.error)
        return vm.to_dict()

    ic(vm)

    chemical = chemical_service.create_chemical(
        session=session,
        name=vm.name,
        active_ingredient=vm.active_ingredient,
        rate_per_100l=vm.rate_per_100l,
        rate_unit=vm.rate_unit,
        chemical_group_ids=vm.chemical_group_ids,
    )

    if chemical:
        # Redirect back to chemical management with success message
        params = urlencode({"success": "Chemical created successfully"})
        response = RedirectResponse(
            url=f"/administration/chemicals?{params}",
            status_code=303,
        )
        response.headers["HX-Push-Url"] = "/administration/chemicals"
        return response

    # Return form with errors
    return vm.to_dict()


@router.get("/chemicals/{chemical_id}/edit")
@require_admin()
@fastapi_chameleon.template("admin/edit_chemical_form.pt")
async def chemicals_edit_get(
    request: Request, chemical_id: int, session: Session = Depends(get_session)
):
    """Display form for editing an existing chemical"""
    vm = EditChemicalViewModel(request, session, chemical_id)
    ic(vm)
    if not vm:
        raise HTTPException(status_code=404, detail="No view model.")
    if vm.error:
        print(vm.error)
        return vm.to_dict()
    return vm.to_dict()


@router.post("/chemicals/{chemical_id}/edit")
@require_admin()
@fastapi_chameleon.template("admin/edit_chemical_form.pt")
async def chemicals_edit_post(
    request: Request,
    chemical_id: int,
    session: Session = Depends(get_session),
):
    vm = EditChemicalViewModel(request, session, chemical_id)

    if not vm:
        raise HTTPException(status_code=404, detail="No view model.")

    await vm.load()

    if vm.error:
        print(vm.error)
        return vm.to_dict()

    ic(vm)

    # Update the chemical
    updated_chemical = chemical_service.update_chemical(
        session=session,
        chemical_id=chemical_id,
        name=vm.name,
        active_ingredient=vm.active_ingredient,
        rate_per_100l=vm.rate_per_100l,
        rate_unit=vm.rate_unit,
        chemical_group_ids=vm.chemical_group_ids,
    )

    if updated_chemical:
        # Redirect back to chemical management with success message
        params = urlencode({"success": "Chemical updated successfully"})
        response = RedirectResponse(
            url=f"/administration/chemicals?{params}",
            status_code=303,
        )
        response.headers["HX-Push-Url"] = "/administration/chemicals"
        return response

    # Return form with errors
    vm.error = "Failed to update chemical"
    return vm.to_dict()


@router.delete("/chemicals/{chemical_id}")
@require_admin()
@fastapi_chameleon.template("admin/chemicals.pt")
async def chemicals_delete(
    request: Request,
    chemical_id: int,
    session: Session = Depends(get_session),
):
    """Delete a chemical"""
    vm = ChemicalManagementViewModel(request, session)

    if not vm:
        raise HTTPException(status_code=404, detail="No view model.")

    # Get the chemical to delete
    chemical_to_delete = chemical_service.get_chemical_by_id(session, chemical_id)
    if not chemical_to_delete:
        vm.error = "Chemical not found"
        return vm.to_dict()

    # Security checks - check if chemical is in use
    if chemical_to_delete.spray_chemicals:
        vm.error = f"Chemical '{chemical_to_delete.name}' cannot be deleted because it is used in spray programs."
        return vm.to_dict()

    # Attempt to delete the chemical
    try:
        deleted = chemical_service.delete_chemical(session, chemical_id)
        if not deleted:
            vm.error = "Failed to delete chemical"
    except Exception as e:
        print(f"Error deleting chemical: {e}")
        vm.error = "An error occurred while deleting the chemical"

    vm = ChemicalManagementViewModel(request, session)

    if not vm:
        raise HTTPException(status_code=404, detail="No view model.")

    vm.set_success(
        message=f"Chemical '{chemical_to_delete.name}' has been deleted successfully"
    )

    return vm.to_dict()
