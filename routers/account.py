import datetime

import fastapi
from fastapi import Depends
from fastapi_chameleon import template
from sqlmodel import Session
from starlette import status
from starlette.requests import Request

from dependencies import get_session
from infrastructure import cookie_auth
from services import user_service
from viewmodels.account.account_viewmodel import AccountViewModel
from viewmodels.account.login_viewmodel import LoginViewModel
from viewmodels.account.register_viewmodel import RegisterViewModel

router = fastapi.APIRouter()


@router.get("/account")
@template()
def index(request: Request, session: Session = Depends(get_session)):
    vm = AccountViewModel(request, session)
    print(vm.to_dict())
    return vm.to_dict()


@router.get("/account/register")
@template()
def register(request: Request, session: Session = Depends(get_session)):
    vm = RegisterViewModel(request, session)
    return vm.to_dict()


@router.post("/account/register")
@template()
async def register(request: Request, session: Session = Depends(get_session)):
    vm = RegisterViewModel(request, session)
    await vm.load()

    if vm.error:
        return vm.to_dict()

    # Create the account

    account = user_service.create_account(session, vm.name, vm.email, vm.password)

    # Login user
    response = fastapi.responses.RedirectResponse(
        url="/account", status_code=status.HTTP_302_FOUND
    )

    print("SETTING AUTH in COOKIE")
    cookie_auth.set_auth(response, account.id)

    return response


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
        "/account", status_code=status.HTTP_302_FOUND
    )
    cookie_auth.set_auth(resp, user.id)

    # TODO update last_login
    user.last_login = datetime.datetime.now()

    return resp


@router.get("/account/logout")
def logout():
    response = fastapi.responses.RedirectResponse(
        url="/", status_code=status.HTTP_302_FOUND
    )
    cookie_auth.logout(response)

    return response
