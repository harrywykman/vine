from decimal import Decimal
from typing import Annotated

import fastapi_chameleon
from fastapi import APIRouter, Depends, Form, HTTPException, Request, responses
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session, selectinload
from sqlmodel import select
from starlette import status

from data.vineyard import Chemical, Spray, SprayChemical, Target
from dependencies import get_session
from services import spray_record_service, spray_service, vineyard_service
from viewmodels.shared.viewmodel import ViewModelBase
from viewmodels.sprays.apply_select_units_form_viewmodel import (
    ApplySelectMUsFormViewModel,
    SelectFormViewModel,
)
from viewmodels.sprays.apply_select_units_submit_viewmodel import (
    ApplySelectUnitsSubmitViewModel,
)
from viewmodels.sprays.create_viewmodel import CreateViewModel
from viewmodels.sprays.form_viewmodel import FormViewModel
from viewmodels.sprays.list_viewmodel import ListViewModel

router = APIRouter()

# HTML routes


## GET List Spray Programs
@router.get("/sprays", response_class=HTMLResponse)
@fastapi_chameleon.template("spray/index.pt")
def spray_index(request: Request, session: Session = Depends(get_session)):
    vm = ListViewModel(request, session)
    if not vm:
        raise HTTPException(status_code=404, detail="No view model.")
    return vm.to_dict()


## GET Chemical Row for Spray Program Form
@router.get("/spray/chemical_row", response_class=HTMLResponse)
@fastapi_chameleon.template("spray/_chemical_row.pt")
def get_chemical_row(session: Session = Depends(get_session)):
    statement = select(Chemical)
    chemicals = session.exec(statement).all()
    targets = [target.value for target in Target]
    if not chemicals:
        raise HTTPException(status_code=404, detail="No chemicals found")
    return {"chemicals": chemicals, "targets": targets}


# TODO refactor to use viewmodel / remove
## GET Editable Spray Program Row
@router.get("/spray/{spray_id}/edit", response_class=HTMLResponse)
@fastapi_chameleon.template("spray/_edit_row.pt")
def get_spray_row_as_form(spray_id: int, session: Session = Depends(get_session)):
    spray = spray_service.eagerly_get_spray_by_id(spray_id, session)

    if not spray:
        raise HTTPException(status_code=404, detail="No chemicals found")

    statement = select(Chemical)
    chemicals = session.exec(statement).all()
    if not chemicals:
        raise HTTPException(status_code=404, detail="No chemicals found")

    return {"sp": spray, "chemicals": chemicals}


# TODO refactor to use viewmodel / remove
## GET Spay program row
@router.get("/spray/{spray_id}/view", response_class=HTMLResponse)
@fastapi_chameleon.template("spray/_display_row.pt")
def spray_view_inline(
    request: Request, spray_id: int, session: Session = Depends(get_session)
):
    spray = spray_service.eagerly_get_spray_by_id(spray_id, session)

    return {"sp": spray}


## GET Spray Form
@router.get("/spray/new/spray_program/{spray_program_id}", response_class=HTMLResponse)
@fastapi_chameleon.template("spray/spray_form.pt")
def spray_spray_program_form(
    request: Request, spray_program_id: int, session: Session = Depends(get_session)
):
    vm = FormViewModel(request, session, spray_program_id=spray_program_id)
    if not vm:
        raise HTTPException(status_code=404, detail="No view model.")
    return vm.to_dict()


# TODO refactor to use viewmodel
## POST Create Spray Program
@router.post("/spray/new")
@fastapi_chameleon.template("spray/spray_form.pt")
async def create_spray(request: Request, session: Session = Depends(get_session)):
    vm = CreateViewModel(request, session)
    await vm.load()

    if not vm:
        raise HTTPException(status_code=404, detail="No view model.")
    if vm.error:
        print(vm.error)
        return vm.to_dict()

    # Create the spray

    spray = spray_service.create_spray(
        session,
        vm.name,
        vm.water_spray_rate_per_hectare,
        vm.chemicals_targets,
        vm.growth_stage_id,
        vm.spray_program_id,
    )

    if not spray:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Spray program not created"
        )

    if vm.error:
        print(vm.error)
        return vm.to_dict()

    if vm.spray_program_id:
        response = responses.RedirectResponse(
            url=f"/spray_programs/{vm.spray_program_id}",
            status_code=status.HTTP_302_FOUND,
        )
    else:
        response = responses.RedirectResponse(
            url="/sprays", status_code=status.HTTP_302_FOUND
        )

    return response


## GET empty template
@router.get("/empty", response_class=HTMLResponse)
@fastapi_chameleon.template("shared/_empty.pt")
def get_no_html():
    return {}


# TODO refactor to use viewmodel
## POST Delete Spray
# TODO use htmx table row fade rather than redirect
@router.post("/spray/{spray_id}/delete")
def delete_vineyard_html(
    spray_id: int,
    session: Session = Depends(get_session),
):
    spray_service.delete_spray(session, spray_id)

    response = responses.RedirectResponse(
        url="/sprays", status_code=status.HTTP_303_SEE_OTHER
    )

    return response


# TODO refactor with ViewModel / resolve refresh required for seeing updated Chemical name or mix rate
@router.post("/spray/{spray_id}/edit", response_class=HTMLResponse)
@fastapi_chameleon.template("spray/_display_row.pt")
async def update_spray(
    spray_id: int,
    request: Request,
    name: str = Form(...),
    water_spray_rate_per_hectare: Decimal = Form(...),
    chemical_ids: list[int] = Form(...),
    mix_rates: list[Decimal] = Form(...),
    session: Session = Depends(get_session),
):
    # Get current spray program with relationships
    sp = session.exec(
        select(Spray)
        .where(Spray.id == spray_id)
        .options(selectinload(Spray.spray_chemicals))
    ).first()

    if not sp:
        raise HTTPException(status_code=404, detail="Spray Program not found")

    sp.name = name
    sp.water_spray_rate_per_hectare = water_spray_rate_per_hectare

    # Delete old chemical associations
    for old_spc in sp.spray_chemicals:
        session.delete(old_spc)
    session.flush()

    # Add new ones
    for chem_id, rate in zip(chemical_ids, mix_rates):
        session.add(
            SprayChemical(spray_id=sp.id, chemical_id=chem_id, mix_rate_per_100L=rate)
        )

    session.commit()

    # ✅ Re-fetch with joined chemical data
    updated_sp = session.exec(
        select(Spray)
        .where(Spray.id == spray_id)
        .options(
            selectinload(Spray.spray_chemicals).selectinload(SprayChemical.chemical)
        )
    ).first()

    return {"sp": updated_sp}


@router.post("/sprays/{spray_id}/add_to_all_units")
@fastapi_chameleon.template("partials/notification.pt")
def add_program_to_all_units(
    request: Request, spray_id: int, session: Session = Depends(get_session)
):
    spray = spray_service.eagerly_get_spray_by_id(spray_id, session)

    if not spray:
        raise HTTPException(status_code=404, detail="Spray not found")

    all_management_units = vineyard_service.get_all_management_units(session)

    for mu in all_management_units:
        if mu.is_active:
            spray_record = spray_record_service.create_or_update_spray_record(
                session, mu.id, spray_id
            )
            session.add(spray_record)
        else:
            print(f"################## Skipped {mu.name} ###################")

    session.commit()

    vm = ViewModelBase(request, session)
    vm.set_success(
        f"Spray program <strong>{spray.name}</strong> applied to all active units."
    )

    return vm.to_dict()


@router.post("/sprays/{spray_id}/add_to_all_reds")
@fastapi_chameleon.template("partials/notification.pt")
def add_program_to_all_red(
    request: Request, spray_id: int, session: Session = Depends(get_session)
):
    spray = spray_service.eagerly_get_spray_by_id(spray_id, session)
    if not spray:
        raise HTTPException(status_code=404, detail="Spray not found")

    red_management_units = vineyard_service.get_red_management_units(session)
    for mu in red_management_units:
        spray_record = spray_record_service.create_or_update_spray_record(
            session, mu.id, spray_id
        )
        session.add(spray_record)
    session.commit()

    vm = ViewModelBase(request, session)
    vm.set_success(
        f"Spray program <strong>{spray.name}</strong> applied to all red units."
    )

    return vm.to_dict()


@router.post("/sprays/{spray_id}/add_to_all_whites")
@fastapi_chameleon.template("partials/notification.pt")
def add_program_to_all_white(
    request: Request, spray_id: int, session: Session = Depends(get_session)
):
    spray = spray_service.eagerly_get_spray_by_id(spray_id, session)
    if not spray:
        raise HTTPException(status_code=404, detail="Spray not found")

    white_management_units = vineyard_service.get_red_management_units(session)
    for mu in white_management_units:
        spray_record = spray_record_service.create_or_update_spray_record(
            session, mu.id, spray_id
        )
        session.add(spray_record)
    session.commit()

    vm = ViewModelBase(request, session)
    vm.set_success(
        f"Spray program <strong>{spray.name}</strong> applied to all white units."
    )

    return vm.to_dict()


@router.get("/sprays/{spray_id}/apply_to_select_units")
@fastapi_chameleon.template("spray/select_mus_for_application.pt")
def apply_to_select_units(
    request: Request, spray_id: int, session: Session = Depends(get_session)
):
    vm = ApplySelectMUsFormViewModel(
        request=request, session=session, spray_id=spray_id
    )

    return vm.to_dict()


@router.post("/sprays/{spray_id}/apply_to_select_units")
@fastapi_chameleon.template("spray/select_mus_for_application.pt")
async def apply_to_select_units_submit(
    request: Request,
    spray_id: int,
    management_unit_ids: Annotated[list[int], Form()],
    session: Session = Depends(get_session),
):
    vm = ApplySelectUnitsSubmitViewModel(
        request=request,
        spray_id=spray_id,
        management_unit_ids=management_unit_ids,
        session=session,
    )

    await vm.load()

    if not vm:
        raise HTTPException(status_code=404, detail="No view model.")

    if vm.error:
        print(f"[Form Error] {vm.error}")
        return vm.to_dict()

    vm.process_submission()

    return vm.to_dict()


@router.get("/sprays/{vineyard_id}/select_all")
@fastapi_chameleon.template("spray/_select_all_mus.pt")
def select_all_vineyard_units(
    request: Request, vineyard_id: int, session: Session = Depends(get_session)
):
    vm = SelectFormViewModel(request=request, session=session, vineyard_id=vineyard_id)

    return vm.to_dict()


@router.get("/sprays/{vineyard_id}/select_none")
@fastapi_chameleon.template("spray/_select_no_mus.pt")
def select_no_vineyard_units(
    request: Request, vineyard_id: int, session: Session = Depends(get_session)
):
    vm = SelectFormViewModel(request=request, session=session, vineyard_id=vineyard_id)

    return vm.to_dict()
