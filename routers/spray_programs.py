from decimal import Decimal
from typing import List, Optional

import fastapi_chameleon
from fastapi import APIRouter, Depends, Form, HTTPException, Request, responses
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from starlette import status

from auth import permissions_decorators
from dependencies import get_session
from services import spray_program_service, spray_service
from viewmodels.spray_programs.create_viewmodel import CreateViewModel
from viewmodels.spray_programs.details_viewmodel import DetailsViewModel
from viewmodels.spray_programs.form_viewmodel import FormViewModel
from viewmodels.spray_programs.list_viewmodel import ListViewModel
from viewmodels.spray_programs.spray_edit_form_viewmodel import SprayEditFormViewModel
from viewmodels.spray_programs.spray_program_spray_delete_viewmodel import (
    SprayDeleteViewModel,
)
from viewmodels.spray_programs.spray_program_spray_update_view_model import (
    SprayUpdateViewModel,
)

router = APIRouter()


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


## POST Delete a Spray for a Spray Program
@router.post("/spray_programs/{spray_program_id}/spray/{spray_id}/delete")
@fastapi_chameleon.template("spray_programs/spray_program_details.pt")
def delete_spray_program_spray(
    request: Request,
    spray_id: int,
    spray_program_id: int,
    session: Session = Depends(get_session),
):
    spray = spray_service.eagerly_get_spray_by_id(session=session, id=spray_id)

    spray_program = spray_program_service.get_spray_program_by_id(
        session=session, spray_program_id=spray_program_id
    )

    vm = SprayDeleteViewModel(
        request=request,
        session=session,
        spray_program_id=spray_program_id,
        spray_id=spray_id,
    )
    if not vm:
        raise HTTPException(status_code=404, detail="No view model.")

    vm.delete_spray()

    if vm.error:
        return vm.to_dict()

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


## GET Edit Spray Form
@router.get(
    "/spray_program/{spray_program_id}/spray/{spray_id}/edit",
    response_class=HTMLResponse,
)
@fastapi_chameleon.template("spray_programs/spray_program_spray_form_edit.pt")
def spray_program_spray_edit_form(
    request: Request,
    spray_id: int,
    spray_program_id: int,
    session: Session = Depends(get_session),
):
    vm = SprayEditFormViewModel(
        request, session, spray_program_id=spray_program_id, spray_id=spray_id
    )
    if not vm:
        raise HTTPException(status_code=404, detail="No view model.")
    return vm.to_dict()


@router.post("/spray_programs/{spray_program_id}/spray/{spray_id}/edit")
@fastapi_chameleon.template("spray_programs/spray_program_spray_form_edit.pt")
async def update_spray_route(
    request: Request,
    spray_id: int,
    spray_program_id: int,
    name: str = Form(...),
    water_spray_rate_per_hectare: int = Form(...),
    growth_stage_id: Optional[int] = Form(...),
    chemical_ids: List[int] = Form([]),
    targets: List[str] = Form([]),
    concentration_factors: List[Decimal] = Form([]),
    session: Session = Depends(get_session),
):
    """
    Route handler for spray edit form submission.
    FastAPI automatically handles the form arrays - chemical_ids, targets, and concentration_factors
    will be matched by their array index.
    """

    # Handle empty growth stage
    growth_stage_id = (
        int(growth_stage_id) if growth_stage_id and growth_stage_id != "" else None
    )

    # Create view model for update
    vm = SprayUpdateViewModel(request, session, spray_id, spray_program_id)

    if vm.error:
        return vm.to_dict()

    # Attempt to update the spray
    vm.update_spray(
        name=name,
        water_spray_rate_per_hectare=water_spray_rate_per_hectare,
        growth_stage_id=growth_stage_id,
        spray_program_id=spray_program_id,
        chemical_ids=chemical_ids,
        targets=targets,
        concentration_factors=concentration_factors,
    )

    return vm.to_dict()
