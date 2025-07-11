from auth.permissions import require_admin, require_role, require_superadmin
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlmodel import Session
from your_auth_module import get_current_user
from your_template_module import render_template

from data.user import User, UserRole
from services.user_service import update_user_role

app = FastAPI()


# API Routes with dependency injection
@app.get("/api/admin/users")
async def get_all_users(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    session: Session = Depends(get_session),
):
    """Only admins and superadmins can view all users"""
    users = session.exec(select(User)).all()
    return {"users": users}


@app.post("/api/admin/users/{user_id}/role")
async def change_user_role(
    user_id: int,
    new_role: UserRole,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    session: Session = Depends(get_session),
):
    """Only admins can change user roles"""
    try:
        updated_user = update_user_role(session, user_id, new_role, current_user)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "Role updated successfully", "user": updated_user}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/superadmin/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_role(UserRole.SUPERADMIN)),
    session: Session = Depends(get_session),
):
    """Only superadmins can delete users"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    session.delete(user)
    session.commit()
    return {"message": "User deleted successfully"}


# Template routes with decorator approach
@app.get("/admin/dashboard", response_class=HTMLResponse)
@require_admin()
async def admin_dashboard(
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Admin dashboard - only accessible to admins and superadmins"""
    users = session.exec(select(User)).all()
    return render_template(
        "admin/dashboard.html",
        {"request": request, "current_user": current_user, "users": users},
    )


@app.get("/superadmin/system", response_class=HTMLResponse)
@require_superadmin()
async def superadmin_system(
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """System management - only accessible to superadmins"""
    return render_template(
        "superadmin/system.html", {"request": request, "current_user": current_user}
    )


# Public route with optional user context
@app.get("/dashboard", response_class=HTMLResponse)
async def user_dashboard(
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """User dashboard - accessible to all authenticated users"""
    return render_template(
        "dashboard.html",
        {
            "request": request,
            "current_user": current_user,
            "is_admin": current_user.is_admin() if current_user else False,
        },
    )
