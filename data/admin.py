from sqladmin import ModelView

from data.user import User
from data.vineyard import (
    Chemical,
    ManagementUnit,
    SprayProgram,
    SprayRecord,
    Status,
    Variety,
    Vineyard,
    WineColour,
)

# User Admin


class UserAdmin(ModelView, model=User):
    column_list = [User.name, User.email]


# Vineyard Admin


class VineyardAdmin(ModelView, model=Vineyard):
    column_list = [Vineyard.name]


class VarietyAdmin(ModelView, model=Variety):
    column_list = [Variety.id, Variety.name]  # type: ignore


class WineColourAdmin(ModelView, model=WineColour):
    column_list = [WineColour.id, WineColour.name]  # type: ignore


class ManagementUnitAdmin(ModelView, model=ManagementUnit):
    column_list = [ManagementUnit.id, ManagementUnit.name]  # type: ignore


class StatusAdmin(ModelView, model=Status):
    column_list = [Status.id, Status.status]  # type: ignore


class SprayProgramAdmin(ModelView, model=SprayProgram):
    column_list = [
        SprayProgram.id,
        SprayProgram.name,
        SprayProgram.water_spray_rate_per_hectare,
    ]  # type: ignore


class SprayRecordAdmin(ModelView, model=SprayRecord):
    column_list = [SprayRecord.id, SprayRecord.operator]  # type: ignore


class ChemicalAdmin(ModelView, model=Chemical):
    column_list = [Chemical.id, Chemical.name, Chemical.active_ingredient]  # type: ignore
