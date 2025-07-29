from decimal import Decimal
from typing import Annotated, Optional

import fastapi
import fastapi_chameleon
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlmodel import Session
from starlette import status

from auth.permissions_decorators import require_operator
from dependencies import get_session
from services import vineyard_service
from viewmodels.vineyards.details_viewmodel import DetailsViewModel
from viewmodels.vineyards.edit_mu_viewmodel import EditMUViewModel
from viewmodels.vineyards.list_viewmodel import ListViewModel
from viewmodels.vineyards.vineyard_spray_record_details import VineyardSprayRecordDetail
from viewmodels.vineyards.vineyard_spray_records_form_edit_viewmodel import (
    VineyardSprayRecordsFormEditViewModel,
)
from viewmodels.vineyards.vineyard_spray_records_form_select_viewmodel import (
    VineyardSprayRecordsFormSelectViewModel,
)
from viewmodels.vineyards.vineyard_spray_records_form_viewmodel import (
    VineyardSprayRecordsFormViewModel,
)
from viewmodels.vineyards.vineyard_spray_records_submit_viewmodel import (
    VineyardSprayRecordsSubmitViewModel,
)

router = APIRouter()
# templates = Jinja2Templates(directory="templates")


# HTML routes


@router.get("/", response_class=HTMLResponse)
@fastapi_chameleon.template("vineyard/index.pt")
def vineyard_index(request: Request, session: Session = Depends(get_session)):
    vm = ListViewModel(request, session)
    return vm.to_dict()


@router.get("/vineyards/{vineyard_id}", response_class=HTMLResponse)
@fastapi_chameleon.template("vineyard/vineyard_details.pt")
def vineyard_details(
    request: Request, vineyard_id: int, session: Session = Depends(get_session)
):
    vm = DetailsViewModel(vineyard_id, request, session)

    return vm.to_dict()


@router.get(
    "/vineyards/{vineyard_id}/spray_records/{spray_id}",
    response_class=HTMLResponse,
)
@fastapi_chameleon.template("vineyard/vineyard_spray_records_form.pt")
def vineyard_spray_records_form(
    request: Request,
    vineyard_id: int,
    spray_id: int,
    session: Session = Depends(get_session),
):
    vm = VineyardSprayRecordsFormViewModel(vineyard_id, spray_id, request, session)

    return vm.to_dict()


@router.get(
    "/vineyards/{vineyard_id}/spray_records/{spray_record_id}/edit",
    response_class=HTMLResponse,
)
@fastapi_chameleon.template("vineyard/vineyard_spray_records_form_edit.pt")
def vineyard_spray_records_form_edit(
    request: Request,
    vineyard_id: int,
    spray_record_id: int,
    session: Session = Depends(get_session),
):
    vm = VineyardSprayRecordsFormEditViewModel(
        vineyard_id, spray_record_id, request, session
    )

    return vm.to_dict()


@router.get("/management_unit/{management_unit_id}/edit", response_class=HTMLResponse)
@fastapi_chameleon.template("management_unit/edit_inline.pt")
def mangement_unit_edit_inline(
    request: Request, management_unit_id: int, session: Session = Depends(get_session)
):
    vm = EditMUViewModel(management_unit_id, request, session)

    return vm.to_dict()


@router.get("/management_unit/{management_unit_id}/view", response_class=HTMLResponse)
@fastapi_chameleon.template("management_unit/display_row.pt")
def mangement_unit_view_inline(
    request: Request, management_unit_id: int, session: Session = Depends(get_session)
):
    vm = EditMUViewModel(management_unit_id, request, session)

    return vm.to_dict()


@router.get("/vineyards", response_class=HTMLResponse)
@require_operator()
@fastapi_chameleon.template("vineyard/vineyard_list.pt")
async def vineyard_list(request: Request, session: Session = Depends(get_session)):
    vm = ListViewModel(request, session)
    return vm.to_dict()


# Spray Record Detail
@router.get("/vineyards/{vineyard_id}/spray_record/{spray_record_id}")
@fastapi_chameleon.template("vineyard/vineyard_spray_record_detail.pt")
async def spray_record_detail(
    spray_record_id: int, request: Request, session: Session = Depends(get_session)
):
    vm = VineyardSprayRecordDetail(spray_record_id, request, session)

    if not vm:
        raise HTTPException(status_code=404, detail="No view model.")
    if vm.error:
        print(vm.error)
        return vm.to_dict()

    return vm.to_dict()


@router.post("/vineyards/{vineyard_id}/spray_records/{spray_id}/submit")
@fastapi_chameleon.template("vineyard/vineyard_spray_records_form.pt")
async def submit_spray_records(
    request: Request,
    vineyard_id: int,
    spray_id: int,
    operator_id: Annotated[int, Form()],
    management_unit_ids: Annotated[list[int], Form()],
    growth_stage_id: Annotated[Optional[int], Form()] = None,
    hours_taken: Annotated[Optional[Decimal], Form()] = None,
    temperature: Annotated[Optional[int], Form()] = None,
    relative_humidity: Annotated[Optional[int], Form()] = None,
    wind_speed: Annotated[Optional[int], Form()] = None,
    wind_direction: Annotated[Optional[str], Form()] = None,
    session: Session = Depends(get_session),
):
    vm = VineyardSprayRecordsSubmitViewModel(
        vineyard_id=vineyard_id,
        spray_id=spray_id,
        operator_id=operator_id,
        growth_stage_id=growth_stage_id,
        hours_taken=hours_taken,
        temperature=temperature,
        relative_humidity=relative_humidity,
        wind_speed=wind_speed,
        wind_direction=wind_direction,
        management_unit_ids=management_unit_ids,
        request=request,
        session=session,
    )

    await vm.load()

    if not vm:
        raise HTTPException(status_code=404, detail="No view model.")

    if vm.error:
        print(f"[Form Error] {vm.error}")
        return vm.to_dict()  # Render back in template using Chameleon

    vm.process_submission()

    if vineyard_service.spray_complete_for_vineyard(
        session=session, spray_id=spray_id, vineyard_id=vineyard_id
    ):
        response = fastapi.responses.RedirectResponse(
            f"/vineyards/{vineyard_id}",
            status_code=status.HTTP_302_FOUND,
        )
        return response

    vm = VineyardSprayRecordsFormViewModel(vineyard_id, spray_id, request, session)

    vm.set_success("Successfully created spray record")

    return vm.to_dict()


@router.get(
    "/vineyards/{vineyard_id}/spray_records/{spray_id}/select_all",
    response_class=HTMLResponse,
)
@fastapi_chameleon.template("vineyard/_vineyard_spray_records_form_select_all.pt")
def vineyard_spray_records_form_select_all(
    request: Request,
    vineyard_id: int,
    spray_id: int,
    session: Session = Depends(get_session),
):
    vm = VineyardSprayRecordsFormSelectViewModel(
        vineyard_id=vineyard_id, spray_id=spray_id, request=request, session=session
    )

    return vm.to_dict()


@router.get(
    "/vineyards/{vineyard_id}/spray_records/{spray_id}/select_none",
    response_class=HTMLResponse,
)
@fastapi_chameleon.template("vineyard/_vineyard_spray_records_form_select_none.pt")
def vineyard_spray_records_form_select_none(
    request: Request,
    vineyard_id: int,
    spray_id: int,
    session: Session = Depends(get_session),
):
    vm = VineyardSprayRecordsFormSelectViewModel(
        vineyard_id=vineyard_id, spray_id=spray_id, request=request, session=session
    )

    return vm.to_dict()
