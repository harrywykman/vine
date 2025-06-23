from sqladmin import ModelView

from data.user import User
from data.vineyard import ManagementUnit, Status, Variety, Vineyard, WineColour

# User Admin


class UserAdmin(ModelView, model=User):
    column_list = [User.name, User.email]


# Vineyard Admin


class VineyardAdmin(ModelView, model=Vineyard):
    column_list = [Vineyard.name]


class VarietyAdmin(ModelView, model=Variety):
    column_list = [Variety.id, Variety.name]


class WineColourAdmin(ModelView, model=WineColour):
    column_list = [WineColour.id, WineColour.name]


class ManagementUnitAdmin(ModelView, model=ManagementUnit):
    column_list = [ManagementUnit.id, ManagementUnit.name]


class StatusAdmin(ModelView, model=Status):
    column_list = [Status.id, Status.status]
