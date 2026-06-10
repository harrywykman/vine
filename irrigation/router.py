import datetime
from decimal import Decimal
from typing import Annotated, Optional

import fastapi
import fastapi_chameleon
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlmodel import Session
from starlette import status

from auth.permissions_decorators import require_admin, require_operator
from dependencies import get_session
from irrigation import irrigation_services
from irrigation.viewmodels.index_viewmodel import IrrigationIndexViewModel
from irrigation.viewmodels.irrigation_block_viewmodel import IrrigationBlockViewModel
from irrigation.viewmodels.programmer_index_viewmodel import ProgrammerIndexViewModel
from irrigation.viewmodels.programming_record_viewmodel import (
    ProgrammingRecordViewModel,
)
from irrigation.viewmodels.schedule_viewmodel import ScheduleViewModel
from irrigation.viewmodels.season_viewmodel import IrrigationSeasonViewModel

router = APIRouter()


# ---------------------------------------------------------------------------
# Season list — irrigation entry point
# ---------------------------------------------------------------------------


@router.get("/irrigation/", response_class=HTMLResponse)
@require_operator()
@fastapi_chameleon.template("irrigation/irrigation_index.pt")
def irrigation_index(request: Request, session: Session = Depends(get_session)):
    vm = IrrigationIndexViewModel(request, session)
    return vm.to_dict()


# ---------------------------------------------------------------------------
# Planner grid — current season overview
# ---------------------------------------------------------------------------


@router.get("/irrigation/season/", response_class=HTMLResponse)
@require_operator()
@fastapi_chameleon.template("irrigation/irrigation_season.pt")
def irrigation_season(request: Request, session: Session = Depends(get_session)):
    vm = IrrigationSeasonViewModel(request, session)
    return vm.to_dict()


# ---------------------------------------------------------------------------
# Schedule — add
# ---------------------------------------------------------------------------


@router.get(
    "/irrigation/schedule/new",
    response_class=HTMLResponse,
)
@require_operator()
@fastapi_chameleon.template("irrigation/irrigation_schedule_form.pt")
def irrigation_schedule_new(
    request: Request,
    management_unit_id: int,  # passed as query param: /irrigation/schedule/new?management_unit_id=x
    session: Session = Depends(get_session),
):
    vm = ScheduleViewModel(
        management_unit_id=management_unit_id,
        request=request,
        session=session,
    )
    return vm.to_dict()


@router.post(
    "/irrigation/schedule/new",
    response_class=HTMLResponse,
)
@require_operator()
@fastapi_chameleon.template("irrigation/irrigation_schedule_form.pt")
def irrigation_schedule_new_submit(
    request: Request,
    management_unit_id: Annotated[int, Form()],
    effective_from: Annotated[datetime.date, Form()],
    applications_per_week: Annotated[int, Form()],
    duration_hours: Annotated[Decimal, Form()],
    notes: Annotated[Optional[str], Form()] = None,
    session: Session = Depends(get_session),
):
    vm = ScheduleViewModel(
        management_unit_id=management_unit_id,
        request=request,
        session=session,
    )

    if vm.error:
        return vm.to_dict()

    if not vm.current_irrigation_season:
        vm.set_error("No active irrigation season.")
        return vm.to_dict()

    irrigation_services.create_schedule(
        session=session,
        management_unit_id=management_unit_id,
        season_id=vm.current_irrigation_season.id,
        effective_from=effective_from,
        applications_per_week=applications_per_week,
        duration_hours=duration_hours,
        created_by_id=vm.user_id,
        notes=notes,
    )

    return fastapi.responses.RedirectResponse(
        url="/irrigation/season/",
        status_code=status.HTTP_302_FOUND,
    )


# ---------------------------------------------------------------------------
# Schedule — edit (correction only)
# ---------------------------------------------------------------------------


@router.get(
    "/irrigation/schedule/{schedule_id}/edit",
    response_class=HTMLResponse,
)
@require_operator()
@fastapi_chameleon.template("irrigation/irrigation_schedule_form.pt")
def irrigation_schedule_edit(
    request: Request,
    schedule_id: int,
    session: Session = Depends(get_session),
):
    schedule = irrigation_services.get_schedule_by_id(session, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found.")

    vm = ScheduleViewModel(
        management_unit_id=schedule.management_unit_id,
        request=request,
        session=session,
        schedule_id=schedule_id,
    )
    return vm.to_dict()


@router.post(
    "/irrigation/schedule/{schedule_id}/edit",
    response_class=HTMLResponse,
)
@require_operator()
@fastapi_chameleon.template("irrigation/irrigation_schedule_form.pt")
def irrigation_schedule_edit_submit(
    request: Request,
    schedule_id: int,
    applications_per_week: Annotated[int, Form()],
    effective_from: Annotated[datetime.date, Form()],
    duration_hours: Annotated[Decimal, Form()],
    effective_until: Annotated[Optional[datetime.date], Form()] = None,
    notes: Annotated[Optional[str], Form()] = None,
    session: Session = Depends(get_session),
):
    schedule = irrigation_services.get_schedule_by_id(session, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found.")

    vm = ScheduleViewModel(
        management_unit_id=schedule.management_unit_id,
        request=request,
        session=session,
        schedule_id=schedule_id,
    )

    if vm.error:
        return vm.to_dict()

    irrigation_services.update_schedule(
        session=session,
        schedule_id=schedule_id,
        applications_per_week=applications_per_week,
        duration_hours=duration_hours,
        notes=notes,
        effective_from=effective_from,
        effective_until=effective_until,
    )

    return fastapi.responses.RedirectResponse(
        url="/irrigation/season/",
        status_code=status.HTTP_302_FOUND,
    )


# ---------------------------------------------------------------------------
# Schedule — close (turn off controller without a replacement schedule)
# ---------------------------------------------------------------------------


@router.post(
    "/irrigation/schedule/{schedule_id}/close",
    response_class=HTMLResponse,
)
@require_operator()
def irrigation_schedule_close(
    request: Request,
    schedule_id: int,
    effective_until: Annotated[datetime.date, Form()],
    session: Session = Depends(get_session),
):
    schedule = irrigation_services.get_schedule_by_id(session, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found.")

    irrigation_services.close_schedule(
        session=session,
        schedule_id=schedule_id,
        effective_until=effective_until,
    )

    return fastapi.responses.RedirectResponse(
        url="/irrigation/season/",
        status_code=status.HTTP_302_FOUND,
    )


# ---------------------------------------------------------------------------
# Season management — admin only
# ---------------------------------------------------------------------------


@router.post("/irrigation/seasons/new", response_class=HTMLResponse)
@require_admin()
def irrigation_season_new(
    request: Request,
    name: Annotated[str, Form()],
    season_start: Annotated[datetime.date, Form()],
    season_end: Annotated[datetime.date, Form()],
    notes: Annotated[Optional[str], Form()] = None,
    session: Session = Depends(get_session),
):
    irrigation_services.create_irrigation_season(
        session=session,
        name=name,
        season_start=season_start,
        season_end=season_end,
        notes=notes,
    )

    return fastapi.responses.RedirectResponse(
        url="/irrigation/",
        status_code=status.HTTP_302_FOUND,
    )


# ---------------------------------------------------------------------------
# Programmer index — list of vineyards to action
# ---------------------------------------------------------------------------


@router.get("/irrigation/program/", response_class=HTMLResponse)
@require_operator()
@fastapi_chameleon.template("irrigation/irrigation_programmer_index.pt")
def irrigation_programmer_index(
    request: Request, session: Session = Depends(get_session)
):
    vm = ProgrammerIndexViewModel(request, session)
    return vm.to_dict()


# ---------------------------------------------------------------------------
# Programmer form — record a controller visit for a vineyard
# ---------------------------------------------------------------------------


@router.get(
    "/irrigation/program/{vineyard_id}",
    response_class=HTMLResponse,
)
@require_operator()
@fastapi_chameleon.template("irrigation/irrigation_programming_form.pt")
def irrigation_programming_form(
    request: Request,
    vineyard_id: int,
    session: Session = Depends(get_session),
):
    vm = ProgrammingRecordViewModel(
        vineyard_id=vineyard_id,
        request=request,
        session=session,
    )
    return vm.to_dict()


@router.post(
    "/irrigation/program/{vineyard_id}",
    response_class=HTMLResponse,
)
@require_operator()
@fastapi_chameleon.template("irrigation/irrigation_programming_form.pt")
def irrigation_programming_form_submit(
    request: Request,
    vineyard_id: int,
    schedule_ids: Annotated[list[int], Form()],
    controller_program_letters: Annotated[list[Optional[str]], Form()] = None,
    controller_notes: Annotated[list[Optional[str]], Form()] = None,
    notes: Annotated[list[Optional[str]], Form()] = None,
    session: Session = Depends(get_session),
):
    """
    Processes one programming record per MU in the vineyard.
    Form fields are submitted as parallel lists indexed by position,
    one entry per schedule_id.
    """
    vm = ProgrammingRecordViewModel(
        vineyard_id=vineyard_id,
        request=request,
        session=session,
    )

    if vm.error:
        return vm.to_dict()

    # Pad optional lists to match schedule_ids length
    letters = controller_program_letters or []
    ctrl_notes = controller_notes or []
    row_notes = notes or []

    for i, schedule_id in enumerate(schedule_ids):
        irrigation_services.create_programming_record(
            session=session,
            schedule_id=schedule_id,
            programmed_by_id=vm.user_id,
            controller_program_letter=letters[i] if i < len(letters) else None,
            controller_note=ctrl_notes[i] if i < len(ctrl_notes) else None,
            notes=row_notes[i] if i < len(row_notes) else None,
        )

    return fastapi.responses.RedirectResponse(
        url="/irrigation/program/",
        status_code=status.HTTP_302_FOUND,
    )


# ---------------------------------------------------------------------------
# Archive season cookie — mirrors spray season pattern
# ---------------------------------------------------------------------------


@router.get("/irrigation/set_viewing_season/{season_id}")
def set_viewing_irrigation_season(
    season_id: int,
    request: Request,
):
    """Set cookie to view an archived irrigation season."""
    response = fastapi.responses.RedirectResponse(
        url="/irrigation/season/",
        status_code=status.HTTP_302_FOUND,
    )
    response.set_cookie("viewing_irrigation_season_id", str(season_id))
    return response


@router.post("/irrigation/clear_viewing_season")
def clear_viewing_irrigation_season(request: Request):
    """Clear the archive cookie, returning to the current season."""
    response = fastapi.responses.RedirectResponse(
        url="/irrigation/season/",
        status_code=status.HTTP_302_FOUND,
    )
    response.delete_cookie("viewing_irrigation_season_id")
    return response


# ---------------------------------------------------------------------------
# Block detail — schedule history, volume stats, emitter configuration
# ---------------------------------------------------------------------------


@router.get(
    "/irrigation/block/{management_unit_id}/",
    response_class=HTMLResponse,
)
@require_operator()
@fastapi_chameleon.template("irrigation/irrigation_block.pt")
def irrigation_block(
    request: Request,
    management_unit_id: int,
    session: Session = Depends(get_session),
):
    vm = IrrigationBlockViewModel(
        management_unit_id=management_unit_id,
        request=request,
        session=session,
    )
    return vm.to_dict()


@router.post(
    "/irrigation/block/{management_unit_id}/emitter/new",
    response_class=HTMLResponse,
)
@require_operator()
def irrigation_emitter_config_new(
    request: Request,
    management_unit_id: int,
    effective_from: Annotated[datetime.date, Form()],
    emitter_spacing_m: Annotated[Decimal, Form()],
    flow_rate_lph: Annotated[Decimal, Form()],
    notes: Annotated[Optional[str], Form()] = None,
    session: Session = Depends(get_session),
):
    vm = IrrigationBlockViewModel(
        management_unit_id=management_unit_id,
        request=request,
        session=session,
    )

    if vm.error:
        return fastapi_chameleon.template("irrigation/irrigation_block.pt")(
            lambda: vm.to_dict()
        )()

    irrigation_services.create_emitter_configuration(
        session=session,
        management_unit_id=management_unit_id,
        effective_from=effective_from,
        emitter_spacing_m=emitter_spacing_m,
        flow_rate_lph=flow_rate_lph,
        recorded_by_id=vm.user_id,
        notes=notes,
    )

    return fastapi.responses.RedirectResponse(
        url=f"/irrigation/block/{management_unit_id}/",
        status_code=status.HTTP_302_FOUND,
    )
