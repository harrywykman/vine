from typing import Optional

from data.vineyard import Vineyard, ManagementUnit
from services import vineyard_service
from starlette.requests import Request
from viewmodels.shared.viewmodel import ViewModelBase


class DetailsViewModel(ViewModelBase):
     def __init__(self, vineyard_id: str, request: Request):
        super().__init__(request)

        self.id: int = vineyard_id
        self.name: Optional[str] = None
        self.address: Optional[str] = None
        self.vineyard: Vineyard = vineyard_service.get_vineyard_by_id(vineyard_id)
        self.management_units: Optiional(List[ManagementUnit]) = vineyard_service.get_vineyard_managment_units_by_id(self.id)

"""     def __init__(self, vineyard_id: int, request: Request):
        super().__init__(request)

        self.package_name = package_name
        self.latest_version = '0.0.0'
        self.is_latest = True
        self.maintainers = []
        self.package: Optional[Package] = None
        self.latest_release: Optional[Release] = None

    async def load(self):
        self.package = await package_service.get_package_by_id(self.package_name)
        self.latest_release = await package_service.get_latest_release_for_package(self.package_name)

        if not self.package or not self.latest_release:
            return

        r = self.latest_release
        self.latest_version = f'{r.major_ver}.{r.minor_ver}.{r.build_ver}' """
