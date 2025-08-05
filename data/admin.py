from sqladmin import ModelView
from sqladmin.fields import AjaxSelectMultipleField
from wtforms.validators import Optional

from data.user import User
from data.vineyard import (
    Chemical,
    ChemicalGroup,
    GrowthStage,
    ManagementUnit,
    Spray,
    SprayChemical,
    SprayProgram,
    SprayRecord,
    SprayRecordChemical,
    Status,
    Variety,
    Vineyard,
    WineColour,
)


# ---------- USER ----------
class UserAdmin(ModelView, model=User):
    column_list = [
        User.id,
        User.name,
        User.email,
        User.role,
        User.created_date,
        User.last_login,
    ]
    column_searchable_list = [User.name, User.email]
    column_filters = [User.role, User.created_date]
    form_columns = [
        User.name,
        User.email,
        User.role,
    ]  # Don't include password hash in form


# ---------- VINEYARD ----------
class VineyardAdmin(ModelView, model=Vineyard):
    column_list = [Vineyard.id, Vineyard.name, Vineyard.address]
    column_searchable_list = [Vineyard.name, Vineyard.address]
    form_columns = [
        Vineyard.name,
        Vineyard.address,
    ]  # Exclude boundary from form (complex geometry)


class VarietyAdmin(ModelView, model=Variety):
    column_list = [Variety.id, Variety.name, Variety.wine_colour_id]
    column_filters = [Variety.wine_colour_id]
    column_searchable_list = [Variety.name]
    form_columns = [Variety.name, Variety.wine_colour_id]

    form_ajax_refs = {"wine_colour": {"fields": [WineColour.name]}}


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
    column_filters = [
        ManagementUnit.vineyard_id,
        ManagementUnit.status_id,
        ManagementUnit.variety_id,
    ]

    # Exclude complex geometry field from form
    form_columns = [
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

    form_ajax_refs = {
        "variety": {"fields": [Variety.name]},
        "vineyard": {"fields": [Vineyard.name]},
        "status": {"fields": [Status.status]},
    }


class StatusAdmin(ModelView, model=Status):
    column_list = [Status.id, Status.status]
    column_searchable_list = [Status.status]
    form_columns = [Status.status]


# ---------- SPRAY PROGRAM ----------
class SprayProgramAdmin(ModelView, model=SprayProgram):
    column_list = [
        SprayProgram.id,
        SprayProgram.name,
        SprayProgram.year_start,
        SprayProgram.year_end,
        SprayProgram.date_created,
    ]

    column_searchable_list = [SprayProgram.name]

    column_filters = [
        SprayProgram.year_start,
        SprayProgram.year_end,
        SprayProgram.date_created,
    ]

    form_columns = [
        SprayProgram.name,
        SprayProgram.year_start,
        SprayProgram.year_end,
    ]


class SprayAdmin(ModelView, model=Spray):
    column_list = [
        Spray.id,
        Spray.name,
        Spray.water_spray_rate_per_hectare,
        Spray.growth_stage_id,
        Spray.spray_program_id,
        Spray.date_created,
    ]
    column_searchable_list = [Spray.name]
    column_filters = [Spray.date_created, Spray.growth_stage_id, Spray.spray_program_id]

    form_columns = [
        Spray.name,
        Spray.water_spray_rate_per_hectare,
        Spray.growth_stage_id,
        Spray.spray_program_id,
    ]

    form_ajax_refs = {
        "growth_stage": {"fields": [GrowthStage.description]},
        "spray_program": {"fields": [SprayProgram.name]},
    }


class SprayRecordAdmin(ModelView, model=SprayRecord):
    column_list = [
        SprayRecord.id,
        SprayRecord.operator_id,
        SprayRecord.complete,
        SprayRecord.date_created,
        SprayRecord.date_completed,
        SprayRecord.growth_stage_id,
        SprayRecord.hours_taken,
        SprayRecord.temperature,
        SprayRecord.relative_humidity,
        SprayRecord.wind_speed,
        SprayRecord.wind_direction,
        SprayRecord.management_unit_id,
        SprayRecord.spray_id,
    ]

    column_searchable_list = []  # Removed operator since it's now operator_id

    column_filters = [
        SprayRecord.complete,
        SprayRecord.date_created,
        SprayRecord.date_completed,
        SprayRecord.operator_id,
        SprayRecord.growth_stage_id,
        SprayRecord.wind_direction,
    ]

    form_columns = [
        SprayRecord.operator_id,
        SprayRecord.complete,
        SprayRecord.date_completed,
        SprayRecord.growth_stage_id,
        SprayRecord.hours_taken,
        SprayRecord.temperature,
        SprayRecord.relative_humidity,
        SprayRecord.wind_speed,
        SprayRecord.wind_direction,
        SprayRecord.management_unit_id,
        SprayRecord.spray_id,
    ]

    form_ajax_refs = {
        "operator": {"fields": [User.name]},
        "growth_stage": {"fields": [GrowthStage.description]},
        "management_unit": {"fields": [ManagementUnit.name]},
        "spray": {"fields": [Spray.name]},
    }


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
            "get_label": lambda group: str(group),
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
    column_list = [
        ChemicalGroup.id,
        ChemicalGroup.name,
        ChemicalGroup.code,
        ChemicalGroup.type,
        ChemicalGroup.moa,
    ]

    column_details_list = [
        ChemicalGroup.id,
        ChemicalGroup.name,
        ChemicalGroup.code,
        ChemicalGroup.type,
        ChemicalGroup.moa,
        ChemicalGroup.chemicals,
    ]

    column_searchable_list = [
        ChemicalGroup.name,
        ChemicalGroup.code,
        ChemicalGroup.moa,
    ]

    column_filters = [
        ChemicalGroup.type,
        ChemicalGroup.code,
    ]

    form_columns = [
        ChemicalGroup.name,
        ChemicalGroup.code,
        ChemicalGroup.type,
        ChemicalGroup.moa,
        ChemicalGroup.chemicals,
    ]

    form_ajax_refs = {
        "chemicals": {
            "fields": [Chemical.name],
        }
    }


class SprayChemicalAdmin(ModelView, model=SprayChemical):
    column_list = [
        SprayChemical.id,
        SprayChemical.spray_id,
        SprayChemical.chemical_id,
        SprayChemical.concentration_factor,
        SprayChemical.target,
    ]
    column_searchable_list = []
    column_filters = [
        SprayChemical.target,
        SprayChemical.spray_id,
        SprayChemical.chemical_id,
    ]
    form_columns = [
        SprayChemical.spray_id,
        SprayChemical.chemical_id,
        SprayChemical.concentration_factor,
        SprayChemical.target,
    ]

    form_ajax_refs = {
        "spray": {"fields": [Spray.name]},
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
        "spray_record": {"fields": [SprayRecord.id]},  # Changed from operator to id
        "chemical": {"fields": [Chemical.name]},
    }
