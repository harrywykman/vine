from urllib.parse import urlencode

import fastapi
from fastapi import Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi_chameleon import template
from sqlmodel import Session
from starlette import status
from starlette.requests import Request

from auth.permissions_decorators import require_user
from dependencies import get_session
from infrastructure import cookie_auth
from services import user_service
from viewmodels.account.account_viewmodel import AccountViewModel
from viewmodels.account.edit_viewmodel import EditViewModel
from viewmodels.account.login_viewmodel import LoginViewModel
from viewmodels.auth.unauthorised_viewmodel import UnauthorisedViewModel

router = fastapi.APIRouter()


@router.get("/account")
@require_user()
@template()
def index(
    request: Request,
    session: Session = Depends(get_session),
    success: str = "",
):
    vm = AccountViewModel(request, session, success=success)
    print(vm.to_dict())
    return vm.to_dict()


@router.get("/account/edit")
@require_user()
@template("account/edit.pt")
def edit(request: Request, session: Session = Depends(get_session)):
    vm = EditViewModel(request, session)
    print(vm.to_dict())
    return vm.to_dict()


@router.post("/account/edit")
@require_user()
@template("account/edit.pt")
async def edit_post(
    request: Request,
    session: Session = Depends(get_session),
):
    vm = EditViewModel(request, session)

    if not vm:
        raise HTTPException(status_code=404, detail="No view model.")

    await vm.load()

    if vm.error:
        print(vm.error)
        return vm.to_dict()

    # Update the user
    updated_user = user_service.update_user(
        session=session,
        user_id=vm.user.id,
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
            url=f"/account?{params}",
            status_code=303,
        )
        response.headers["HX-Push-Url"] = "/account"
        return response

    # Return form with errors
    vm.error = "Failed to update user"
    return vm.to_dict()


# @router.get("/account/register")
# @require_admin()
# @template()
# def register(request: Request, session: Session = Depends(get_session)):
#    vm = RegisterViewModel(request, session)
##    return vm.to_dict()


# @router.post("/account/register")
# @require_admin()
# @template()
# async def register(request: Request, session: Session = Depends(get_session)):
#    vm = RegisterViewModel(request, session)
#    await vm.load()

#    if vm.error:
#        return vm.to_dict()

# Create the account

#    account = user_service.create_account(session, vm.name, vm.email, vm.password)

# Login user
#    response = fastapi.responses.RedirectResponse(
#        url="/account", status_code=status.HTTP_302_FOUND
#    )

#    print("SETTING AUTH in COOKIE")
#    cookie_auth.set_auth(response, account.id)

#    return response


# ################### LOGIN #################################


@router.get("/account/login")
@template(template_file="account/login.pt")
def login_get(request: Request, session: Session = Depends(get_session)):
    vm = LoginViewModel(request, session)
    return vm.to_dict()


@router.post("/account/login")
@template(template_file="account/login.pt")
async def login_post(request: Request, session: Session = Depends(get_session)):
    vm = LoginViewModel(request, session)
    await vm.load()

    if vm.error:
        return vm.to_dict()

    user = user_service.login_user(session, vm.email, vm.password)
    if not user:
        vm.error = "The account does not exist or the password is wrong."
        return vm.to_dict()

    resp = fastapi.responses.RedirectResponse(
        "/vineyards", status_code=status.HTTP_302_FOUND
    )
    cookie_auth.set_auth(resp, user.id)

    return resp


@router.get("/account/logout")
def logout():
    response = fastapi.responses.RedirectResponse(
        url="/", status_code=status.HTTP_302_FOUND
    )
    cookie_auth.logout(response)

    return response


@router.get("/unauthorised", response_class=HTMLResponse)
@template(template_file="shared/unauthorised.pt")
async def unauthorised(request: Request, session: Session = Depends(get_session)):
    vm = UnauthorisedViewModel(request, session)
    vm.message = "You don't have permission to access this resource."

    return vm.to_dict()
