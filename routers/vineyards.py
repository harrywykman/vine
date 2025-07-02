from decimal import Decimal
from typing import Annotated, Optional

import fastapi_chameleon
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlmodel import Session

from dependencies import get_session
from viewmodels.vineyards.details_viewmodel import DetailsViewModel
from viewmodels.vineyards.edit_mu_viewmodel import EditMUViewModel
from viewmodels.vineyards.list_viewmodel import ListViewModel
from viewmodels.vineyards.vineyard_spray_record_details import VineyardSprayRecordDetail
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
    "/vineyards/{vineyard_id}/spray_records/{spray_program_id}",
    response_class=HTMLResponse,
)
@fastapi_chameleon.template("vineyard/vineyard_spray_records_form.pt")
def vineyard_spray_records_form(
    request: Request,
    vineyard_id: int,
    spray_program_id: int,
    session: Session = Depends(get_session),
):
    vm = VineyardSprayRecordsFormViewModel(
        vineyard_id, spray_program_id, request, session
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
@fastapi_chameleon.template("vineyard/vineyard_list.pt")
def vineyard_list(request: Request, session: Session = Depends(get_session)):
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


@router.post("/vineyards/{vineyard_id}/spray_records/{spray_program_id}/submit")
@fastapi_chameleon.template("vineyard/vineyard_spray_records_form.pt")
async def submit_spray_records(
    request: Request,
    vineyard_id: int,
    spray_program_id: int,
    operator: Annotated[str, Form()],
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
        spray_program_id=spray_program_id,
        operator=operator,
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

    return RedirectResponse(
        url=f"/vineyards/{vineyard_id}",
        status_code=303,
    )


""" @router.post("/vineyards/{vineyard_id}/spray_records/{spray_program_id}/submit")
async def submit_spray_records(
    vineyard_id: int,
    spray_program_id: int,
    operator: Annotated[str, Form(...)],
    growth_stage_id: Annotated[int | None, Form(None)],
    hours_taken: Annotated[Decimal | None, Form(None)],
    temperature: Annotated[int | None, Form(None)],
    relative_humidity: Annotated[int | None, Form(None)],
    wind_speed: Annotated[int | None, Form(None)],
    wind_direction: Annotated[str | None, Form(None)],
    management_unit_ids: Annotated[list[int], Form(...)],
    request: Request,
    session: Session = Depends(get_session),
):
    vm = VineyardSprayRecordsSubmitViewModel(
        vineyard_id=vineyard_id,
        spray_program_id=spray_program_id,
        operator=operator,
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

    await vm.load_dynamic_fields()  # fetch batch numbers from request.form()
    vm.process_submission()

    return RedirectResponse(
        url=f"/vineyards/{vineyard_id}/spray_records/{spray_program_id}",
        status_code=303,
    )


@router.post("/vineyards/{vineyard_id}/spray_records/{spray_program_id}/submit")
async def submit_spray_records(
    request: Request,
    vineyard_id: int,
    spray_program_id: int,
    operator: str = Form(...),
    growth_stage_id: int | None = Form(None),
    hours_taken: Decimal | None = Form(None),
    temperature: int | None = Form(None),
    relative_humidity: int | None = Form(None),
    wind_speed: int | None = Form(None),
    wind_direction: str | None = Form(None),
    management_unit_ids: list[int] = Form(
        ...
    ),  # Will work if multiple checkboxes named "management_unit_ids"
    session: Session = Depends(get_session),
):
    form = await request.form()

    # Fetch SprayProgramChemicals for this program
    program_chems = session.exec(
        select(SprayProgramChemical).where(
            SprayProgramChemical.spray_program_id == spray_program_id
        )
    ).all()

    # Map chemical_id -> batch_number from form
    chem_batch_map = {}
    for pc in program_chems:
        key = f"batch_number_{pc.chemical_id}"
        batch_number = form.get(key)
        if not batch_number:
            raise HTTPException(
                status_code=400,
                detail=f"Missing batch number for chemical {pc.chemical.name}",
            )
        chem_batch_map[pc.chemical_id] = batch_number

    # Convert wind_direction string to enum if provided
    wd_enum = None
    if wind_direction:
        try:
            wd_enum = WindDirection[wind_direction]
        except KeyError:
            raise HTTPException(status_code=400, detail="Invalid wind direction")

    # Process each selected management unit's spray record
    for mu_id in management_unit_ids:
        spray_record = session.exec(
            select(SprayRecord).where(
                SprayRecord.management_unit_id == mu_id,
                SprayRecord.spray_program_id == spray_program_id,
            )
        ).first()

        if not spray_record:
            continue  # Or optionally raise an error?

        spray_record.operator = operator
        spray_record.growth_stage_id = growth_stage_id
        spray_record.hours_taken = hours_taken
        spray_record.temperature = temperature
        spray_record.relative_humidity = relative_humidity
        spray_record.wind_speed = wind_speed
        spray_record.wind_direction = wd_enum
        spray_record.complete = True
        spray_record.date_completed = datetime.datetime.now()

        # Add new SprayRecordChemicals with batch numbers
        for chem_id, batch_number in chem_batch_map.items():
            src = SprayRecordChemical(
                spray_record_id=spray_record.id,
                chemical_id=chem_id,
                batch_number=batch_number,
            )
            session.add(src)

        session.add(spray_record)

    session.commit()

    return RedirectResponse(
        url=f"/vineyards/{vineyard_id}/spray_records/{spray_program_id}",
        status_code=303,
    )
 """
