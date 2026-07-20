import datetime
from typing import Annotated, Optional

import fastapi
import fastapi_chameleon
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from sqlmodel import Session
from starlette import status

from auth.permissions_decorators import require_operator
from dependencies import get_session
from monitoring import monitoring_services
from monitoring.form_config import DISEASE_TARGET_ORDER
from monitoring.viewmodels.monitoring_record_form_viewmodel import (
    MonitoringRecordFormViewModel,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# Monitoring record — new (diseases only, first pass)
# ---------------------------------------------------------------------------


@router.get(
    "/monitoring/new",
    response_class=HTMLResponse,
)
@require_operator()
@fastapi_chameleon.template("monitoring/monitoring_record_form.pt")
def monitoring_record_new(
    request: Request,
    management_unit_id: int,  # /monitoring/new?management_unit_id=x
    session: Session = Depends(get_session),
):
    vm = MonitoringRecordFormViewModel(
        management_unit_id=management_unit_id,
        request=request,
        session=session,
    )
    return vm.to_dict()


@router.post(
    "/monitoring/new",
    response_class=HTMLResponse,
)
@require_operator()
@fastapi_chameleon.template("monitoring/monitoring_record_form.pt")
def monitoring_record_new_submit(
    request: Request,
    management_unit_id: Annotated[int, Form()],
    monitoring_date: Annotated[datetime.date, Form()],
    growth_stage_id: Annotated[Optional[int], Form()] = None,
    # Parallel lists, one entry per DISEASE_TARGET_ORDER position. A target
    # whose section was never expanded simply won't appear in these lists
    # once the form only submits fields for expanded/lazy-loaded sections —
    # for now (single-partial, no HTMX lazy-load yet) every disease field
    # always posts, blank or not, so blank entries are filtered in the
    # service layer instead. See save_disease_observations().
    disease_targets: Annotated[list[str], Form()] = None,
    disease_presence: Annotated[list[Optional[str]], Form()] = None,
    disease_severity: Annotated[list[Optional[str]], Form()] = None,
    session: Session = Depends(get_session),
):
    vm = MonitoringRecordFormViewModel(
        management_unit_id=management_unit_id,
        request=request,
        session=session,
    )

    if vm.error:
        return vm.to_dict()

    record = monitoring_services.create_monitoring_record(
        session=session,
        management_unit_id=management_unit_id,
        observer_id=vm.user_id,
        monitoring_date=monitoring_date,
        growth_stage_id=growth_stage_id,
    )

    targets = disease_targets or [t.value for t in DISEASE_TARGET_ORDER]
    presences = disease_presence or []
    severities = disease_severity or []

    created_count = monitoring_services.save_disease_observations(
        session=session,
        monitoring_record_id=record.id,
        targets=targets,
        presences=presences,
        severities=severities,
    )

    return fastapi.responses.RedirectResponse(
        url=(
            f"/monitoring/new?management_unit_id={management_unit_id}"
            f"&created={created_count}"
        ),
        status_code=status.HTTP_302_FOUND,
    )
