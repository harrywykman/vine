from sqladmin import ModelView

from models.vineyard import ManagementUnit, Variety, Vineyard, WineColour


class VineyardAdmin(ModelView, model=Vineyard):
    column_list = [Vineyard.name]


class VarietyAdmin(ModelView, model=Variety):
    column_list = [Variety.id, Variety.name, Variety.clone_name]


class WineColourAdmin(ModelView, model=WineColour):
    column_list = [WineColour.id, WineColour.name]


class ManagementUnitAdmin(ModelView, model=ManagementUnit):
    column_list = [ManagementUnit.id, ManagementUnit.name]
