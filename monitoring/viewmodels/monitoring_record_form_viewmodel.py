import datetime

from sqlmodel import Session
from starlette.requests import Request

from data.vineyard import ManagementUnit
from monitoring.form_config import DISEASE_SECTIONS
from monitoring.models import Presence, Severity
from services import vineyard_service
from viewmodels.shared.viewmodel import ViewModelBase


class MonitoringRecordFormViewModel(ViewModelBase):
    """
    Viewmodel for creating a monitoring record with disease observations.

    First pass: diseases only. Snails / weevils / mites / mealy bug /
    caterpillars / beneficials / general observations will each get their
    own partial + section list (mirroring DISEASE_SECTIONS) in later passes,
    at which point this viewmodel will grow one more list attribute per
    category rather than needing a rewrite.
    """

    def __init__(
        self,
        management_unit_id: int,
        request: Request,
        session: Session,
    ):
        super().__init__(request, session)

        self.management_unit_id = management_unit_id
        self.management_unit: ManagementUnit | None = session.get(
            ManagementUnit, management_unit_id
        )

        if not self.management_unit:
            self.set_error("Management unit not found.")

        self.growth_stages = vineyard_service.all_growth_stages(session)

        self.monitoring_date: datetime.date = datetime.date.today()

        # Section config the template iterates over to render the
        # collapsible Diseases group. See form_config.py.
        self.disease_sections = DISEASE_SECTIONS
        self.presence_options = list(Presence)
        self.severity_options = list(Severity)

        # Set by the redirect after a successful POST (see router.py).
        # Query param rather than a session flash, matching how the rest of
        # the app has no flash-message infrastructure yet.
        created = request.query_params.get("created")
        if created is not None:
            count = int(created)
            noun = "observation" if count == 1 else "observations"
            self.set_success(
                f"{count} {noun} recorded."
                if count > 0
                else "Monitoring record saved — no observations recorded."
            )
