from decimal import Decimal

import fastapi_chameleon
from fastapi import APIRouter, Depends, Form, HTTPException, Request, responses
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session, selectinload
from sqlmodel import select
from starlette import status

from data.vineyard import Chemical, SprayProgram, SprayProgramChemical
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


## GET Editable Spray Program Row
@router.get("/spray_program/{spray_program_id}/edit", response_class=HTMLResponse)
@fastapi_chameleon.template("spray_program/_edit_row.pt")
def get_spray_program_row_as_form(
    spray_program_id: int, session: Session = Depends(get_session)
):
    spray_program = spray_program_service.eagerly_get_spray_program_by_id(
        spray_program_id, session
    )

    if not spray_program:
        raise HTTPException(status_code=404, detail="No chemicals found")

    statement = select(Chemical)
    chemicals = session.exec(statement).all()
    if not chemicals:
        raise HTTPException(status_code=404, detail="No chemicals found")

    return {"sp": spray_program, "chemicals": chemicals}


## GET Spay program row
@router.get("/spray_program/{spray_program_id}/view", response_class=HTMLResponse)
@fastapi_chameleon.template("spray_program/_display_row.pt")
def spray_program_view_inline(
    request: Request, spray_program_id: int, session: Session = Depends(get_session)
):
    spray_program = spray_program_service.eagerly_get_spray_program_by_id(
        spray_program_id, session
    )

    return {"sp": spray_program}


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


# TODO refactor with ViewModel / resolve refresh required for seeing updated Chemical name or mix rate
@router.post("/spray_program/{spray_program_id}/edit", response_class=HTMLResponse)
@fastapi_chameleon.template("spray_program/_display_row.pt")
async def update_spray_program(
    spray_program_id: int,
    request: Request,
    name: str = Form(...),
    water_spray_rate_per_hectare: Decimal = Form(...),
    chemical_ids: list[int] = Form(...),
    mix_rates: list[Decimal] = Form(...),
    session: Session = Depends(get_session),
):
    # Get current spray program with relationships
    sp = session.exec(
        select(SprayProgram)
        .where(SprayProgram.id == spray_program_id)
        .options(selectinload(SprayProgram.spray_program_chemicals))
    ).first()

    if not sp:
        raise HTTPException(status_code=404, detail="Spray Program not found")

    sp.name = name
    sp.water_spray_rate_per_hectare = water_spray_rate_per_hectare

    # Delete old chemical associations
    for old_spc in sp.spray_program_chemicals:
        session.delete(old_spc)
    session.flush()

    # Add new ones
    for chem_id, rate in zip(chemical_ids, mix_rates):
        session.add(
            SprayProgramChemical(
                spray_program_id=sp.id, chemical_id=chem_id, mix_rate_per_100L=rate
            )
        )

    session.commit()

    # ✅ Re-fetch with joined chemical data
    updated_sp = session.exec(
        select(SprayProgram)
        .where(SprayProgram.id == spray_program_id)
        .options(
            selectinload(SprayProgram.spray_program_chemicals).selectinload(
                SprayProgramChemical.chemical
            )
        )
    ).first()

    return {"sp": updated_sp}
