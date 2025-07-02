from sqladmin import ModelView
from sqladmin.fields import AjaxSelectMultipleField
from wtforms.validators import Optional

from data.user import User
from data.vineyard import (
    Chemical,
    ChemicalGroup,
    GrowthStage,
    ManagementUnit,
    SprayProgram,
    SprayProgramChemical,
    SprayRecord,
    SprayRecordChemical,
    Status,
    Variety,
    Vineyard,
    WineColour,
)


# ---------- USER ----------
class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.name, User.email]
    column_searchable_list = [User.name, User.email]
    form_columns = [User.name, User.email]


# ---------- VINEYARD ----------
class VineyardAdmin(ModelView, model=Vineyard):
    column_list = [Vineyard.id, Vineyard.name, Vineyard.address]
    column_searchable_list = [Vineyard.name, Vineyard.address]
    form_columns = [Vineyard.name, Vineyard.address]


class VarietyAdmin(ModelView, model=Variety):
    column_list = [Variety.id, Variety.name, Variety.wine_colour_id]
    column_filters = [Variety.wine_colour_id]
    column_searchable_list = [Variety.name]
    form_columns = [Variety.name, Variety.wine_colour_id]


class WineColourAdmin(ModelView, model=WineColour):
    column_list = [WineColour.id, WineColour.name]
    column_searchable_list = [WineColour.name]
    form_columns = [WineColour.name]


class ManagementUnitAdmin(ModelView, model=ManagementUnit):
    column_list = [
        ManagementUnit.id,
        ManagementUnit.name,
        ManagementUnit.variety_name_modifier,
        ManagementUnit.area,
        ManagementUnit.row_width,
        ManagementUnit.vine_spacing,
        ManagementUnit.rows_total,
        ManagementUnit.rows_start_number,
        ManagementUnit.rows_end_number,
        ManagementUnit.date_planted,
        ManagementUnit.variety_id,
        ManagementUnit.vineyard_id,
        ManagementUnit.status_id,
    ]
    column_searchable_list = [ManagementUnit.name, ManagementUnit.variety_name_modifier]
    column_filters = [ManagementUnit.vineyard_id, ManagementUnit.status_id]
    form_columns = column_list  # All editable


class StatusAdmin(ModelView, model=Status):
    column_list = [Status.id, Status.status]
    column_searchable_list = [Status.status]
    form_columns = [Status.status]


# ---------- SPRAY PROGRAM ----------
class SprayProgramAdmin(ModelView, model=SprayProgram):
    column_list = [
        SprayProgram.id,
        SprayProgram.name,
        SprayProgram.water_spray_rate_per_hectare,
        SprayProgram.date_created,
    ]
    column_searchable_list = [SprayProgram.name]
    column_filters = [SprayProgram.date_created]
    form_columns = [
        SprayProgram.name,
        SprayProgram.water_spray_rate_per_hectare,
    ]


class SprayRecordAdmin(ModelView, model=SprayRecord):
    column_list = [
        SprayRecord.id,
        SprayRecord.operator,
        SprayRecord.complete,
        SprayRecord.date_created,
        SprayRecord.management_unit_id,
        SprayRecord.spray_program_id,
    ]
    column_searchable_list = [SprayRecord.operator]
    column_filters = [SprayRecord.complete, SprayRecord.date_created]
    form_columns = [
        SprayRecord.operator,
        SprayRecord.complete,
        SprayRecord.management_unit_id,
        SprayRecord.spray_program_id,
    ]


class ChemicalAdmin(ModelView, model=Chemical):
    column_list = [
        Chemical.id,
        Chemical.name,
        Chemical.active_ingredient,
        Chemical.rate_per_100l,
        Chemical.rate_unit,
    ]

    column_searchable_list = [Chemical.name, Chemical.active_ingredient]
    column_filters = [Chemical.rate_unit]

    form_columns = [
        Chemical.name,
        Chemical.active_ingredient,
        Chemical.rate_per_100l,
        Chemical.rate_unit,
        Chemical.chemical_groups,
    ]

    form_overrides = {
        Chemical.chemical_groups: AjaxSelectMultipleField,
    }

    form_args = {
        Chemical.chemical_groups: {
            "label": "Chemical Groups",
            "query_factory": lambda: ChemicalGroup.select().order_by(
                ChemicalGroup.code
            ),
            "get_label": lambda group: str(group),  # uses __str__ output
            "validators": [Optional()],
        }
    }


class GrowthStageAdmin(ModelView, model=GrowthStage):
    column_list = [
        GrowthStage.id,
        GrowthStage.el_number,
        GrowthStage.description,
        GrowthStage.is_major,
    ]
    column_searchable_list = [
        GrowthStage.el_number,
        GrowthStage.description,
    ]
    column_filters = [
        GrowthStage.el_number,
        GrowthStage.is_major,
    ]
    form_columns = [
        GrowthStage.el_number,
        GrowthStage.description,
        GrowthStage.is_major,
    ]


class ChemicalGroupAdmin(ModelView, model=ChemicalGroup):
    # List view columns
    column_list = [
        ChemicalGroup.id,
        ChemicalGroup.name,
        ChemicalGroup.code,
        ChemicalGroup.type,
        ChemicalGroup.moa,
    ]

    # Detail view columns (includes related chemicals)
    column_details_list = [
        ChemicalGroup.id,
        ChemicalGroup.name,
        ChemicalGroup.code,
        ChemicalGroup.type,
        ChemicalGroup.moa,
        ChemicalGroup.chemicals,  # Display related chemicals
    ]

    # Searchable fields
    column_searchable_list = [
        ChemicalGroup.name,
        ChemicalGroup.code,
        ChemicalGroup.moa,
    ]

    # Filters
    column_filters = [
        ChemicalGroup.type,
        ChemicalGroup.code,
    ]

    # Form columns
    form_columns = [
        ChemicalGroup.name,
        ChemicalGroup.code,
        ChemicalGroup.type,
        ChemicalGroup.moa,
        ChemicalGroup.chemicals,  # Editable many-to-many relation
    ]

    # Optional: Allow autocompletion for related chemicals
    form_ajax_refs = {
        "chemicals": {
            "fields": [Chemical.name],
        }
    }


class SprayProgramChemicalAdmin(ModelView, model=SprayProgramChemical):
    column_list = [
        SprayProgramChemical.id,
        SprayProgramChemical.spray_program_id,
        SprayProgramChemical.chemical_id,
        SprayProgramChemical.concentration_factor,
        SprayProgramChemical.target,
    ]
    column_searchable_list = []
    column_filters = [
        SprayProgramChemical.target,
        SprayProgramChemical.spray_program_id,
        SprayProgramChemical.chemical_id,
    ]
    form_columns = [
        SprayProgramChemical.spray_program_id,
        SprayProgramChemical.chemical_id,
        SprayProgramChemical.concentration_factor,
        SprayProgramChemical.target,
    ]

    form_ajax_refs = {
        "spray_program": {"fields": [SprayProgram.name]},
        "chemical": {"fields": [Chemical.name]},
    }


class SprayRecordChemicalAdmin(ModelView, model=SprayRecordChemical):
    column_list = [
        SprayRecordChemical.id,
        SprayRecordChemical.spray_record_id,
        SprayRecordChemical.chemical_id,
        SprayRecordChemical.batch_number,
    ]

    column_filters = [
        SprayRecordChemical.spray_record_id,
        SprayRecordChemical.chemical_id,
    ]

    form_columns = [
        SprayRecordChemical.spray_record_id,
        SprayRecordChemical.chemical_id,
        SprayRecordChemical.batch_number,
    ]

    form_ajax_refs = {
        "spray_record": {"fields": [SprayRecord.operator]},
        "chemical": {"fields": [Chemical.name]},
    }
