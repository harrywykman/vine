import fastapi_chameleon
from fastapi import APIRouter, Depends, HTTPException, Request, responses
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlmodel import select
from starlette import status

from data.vineyard import Chemical
from dependencies import get_session
from services import spray_program_service
from viewmodels.spray_programs.create_viewmodel import CreateViewModel
from viewmodels.spray_programs.details_viewmodel import DetailsViewModel
from viewmodels.spray_programs.list_viewmodel import ListViewModel

router = APIRouter()

# HTML routes


## GET List Spray Programs
@router.get("/spray_programs", response_class=HTMLResponse)
@fastapi_chameleon.template("spray_program/index.pt")
def spray_program_index(request: Request, session: Session = Depends(get_session)):
    vm = ListViewModel(request, session)
    if not vm:
        raise HTTPException(status_code=404, detail="No view model.")
    return vm.to_dict()


## GET Chemical Row for Spray Program Form
@router.get("/spray_program/chemical_row", response_class=HTMLResponse)
@fastapi_chameleon.template("spray_program/_chemical_row.pt")
def get_chemical_row(session: Session = Depends(get_session)):
    statement = select(Chemical)
    chemicals = session.exec(statement).all()
    if not chemicals:
        raise HTTPException(status_code=404, detail="No chemicals found")
    return {"chemicals": chemicals}


## GET Spray Program Form
@router.get("/spray_program/new", response_class=HTMLResponse)
@fastapi_chameleon.template("spray_program/spray_program_form.pt")
def spray_program_index(request: Request, session: Session = Depends(get_session)):
    vm = DetailsViewModel(None, request, session)
    if not vm:
        raise HTTPException(status_code=404, detail="No view model.")
    return vm.to_dict()


## POST Create Spray Program
@router.post("/spray_program/new")
@fastapi_chameleon.template("spray_program/spray_program_form.pt")
async def create_spray_program(
    request: Request, session: Session = Depends(get_session)
):
    vm = CreateViewModel(request, session)
    await vm.load()

    if not vm:
        raise HTTPException(status_code=404, detail="No view model.")
    if vm.error:
        print(vm.error)
        return vm.to_dict()

    # Create the spray_program

    spray_program = spray_program_service.create_spray_program(
        session, vm.name, vm.water_spray_rate_per_hectare, vm.chemicals_mix_rates
    )

    if not spray_program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Spray program not created"
        )

    response = responses.RedirectResponse(
        url="/spray_programs", status_code=status.HTTP_302_FOUND
    )
    return response


## GET empty template
@router.get("/empty", response_class=HTMLResponse)
@fastapi_chameleon.template("shared/_empty.pt")
def get_no_html():
    return {}


## POST Delete Spray Program
# TODO use htmx table row fade rather than redirect
@router.post("/spray_program/{spray_program_id}/delete")
def delete_vineyard_html(
    spray_program_id: int,
    session: Session = Depends(get_session),
):
    spray_program_service.delete_spray_program(session, spray_program_id)

    response = responses.RedirectResponse(
        url="/spray_programs", status_code=status.HTTP_303_SEE_OTHER
    )

    return response
