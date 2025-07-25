import fastapi_chameleon
from fastapi import APIRouter, Depends, HTTPException, Request, responses
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from starlette import status

from dependencies import get_session
from services import spray_program_service
from viewmodels.spray_programs.create_viewmodel import CreateViewModel
from viewmodels.spray_programs.details_viewmodel import DetailsViewModel
from viewmodels.spray_programs.form_viewmodel import FormViewModel
from viewmodels.spray_programs.list_viewmodel import ListViewModel

router = APIRouter()

from auth import permissions_decorators

# HTML routes


## GET List Spray Programs
@router.get("/spray_programs", response_class=HTMLResponse)
@fastapi_chameleon.template("spray_programs/index.pt")
def spray_program_index(request: Request, session: Session = Depends(get_session)):
    vm = ListViewModel(request, session)
    if not vm:
        raise HTTPException(status_code=404, detail="No view model.")
    return vm.to_dict()


## GET Spray Program Details
@router.get("/spray_programs/{spray_program_id}", response_class=HTMLResponse)
@fastapi_chameleon.template("spray_programs/spray_program_details.pt")
def spray_program_details(
    request: Request,
    spray_program_id: int,
    session: Session = Depends(get_session),
):
    vm = DetailsViewModel(request, session, spray_program_id=spray_program_id)
    if not vm:
        raise HTTPException(status_code=404, detail="No view model.")
    return vm.to_dict()


## GET Spray Program Form
@router.get("/spray_program/new", response_class=HTMLResponse)
@permissions_decorators.require_admin()
@fastapi_chameleon.template("spray_programs/spray_program_form.pt")
async def spray_program_form(request: Request, session: Session = Depends(get_session)):
    vm = FormViewModel(request, session)
    if not vm:
        raise HTTPException(status_code=404, detail="No view model.")
    return vm.to_dict()


## POST Create Spray Program
@router.post("/spray_program/new")
@permissions_decorators.require_admin()
@fastapi_chameleon.template("spray_programs/spray_program_form.pt")
async def create_spray(request: Request, session: Session = Depends(get_session)):
    vm = CreateViewModel(request, session)
    await vm.load()

    if not vm:
        raise HTTPException(status_code=404, detail="No view model.")
    if vm.error:
        print(vm.error)
        return vm.to_dict()

    # Create the spray

    spray_program = spray_program_service.create_spray_program(
        session,
        name=vm.name,
        year_start=vm.year_start,
        year_end=vm.year_end,
    )

    if not spray_program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Spray program not created"
        )

    if vm.error:
        print(vm.error)
        return vm.to_dict()

    response = responses.RedirectResponse(
        url="/spray_programs", status_code=status.HTTP_302_FOUND
    )
    return response
