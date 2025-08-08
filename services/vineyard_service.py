import re
from typing import List

from fastapi import HTTPException, status
from icecream import ic
from sqlalchemy import asc, func
from sqlalchemy.orm import joinedload, selectinload
from sqlmodel import Session, select

from data.vineyard import (
    Chemical,
    GrowthStage,
    ManagementUnit,
    Spray,
    SprayChemical,
    SprayRecord,
    SprayRecordChemical,
    Variety,
    Vineyard,
    WineColour,
)


def custom_sort_key_management_unit(management_unit: ManagementUnit):
    if management_unit.name.isdigit():
        return int(management_unit.name)
    elif re.search(r"\d+", management_unit.name) == None:
        return 999
    else:
        return int(re.search(r"\d+", management_unit.name).group())


def sort_mus(vineyard: Vineyard) -> Vineyard:
    vineyard.management_units.sort(
        key=lambda management_unit: custom_sort_key_management_unit(
            management_unit=management_unit
        )
    )
    return vineyard


def all_vineyards(session: Session) -> List[Vineyard]:
    query = select(Vineyard).order_by(Vineyard.name)

    vineyards = session.exec(query).all()

    for vineyard in vineyards:
        sort_mus(vineyard=vineyard)

    return vineyards


def all_vineyards_with_mangement_units(session: Session):
    statement = (
        select(Vineyard)
        .order_by(Vineyard.name)
        .options(
            selectinload(Vineyard.management_units)
            .selectinload(ManagementUnit.variety)
            .selectinload(Variety.wine_colour),
        )
    )

    vineyards = session.exec(statement).all()
    for vineyard in vineyards:
        sort_mus(vineyard=vineyard)
    return vineyards


def get_vineyard_by_id(session: Session, id: int):
    print("GETTING VINEYARD BY ID")
    vineyard = session.get(Vineyard, id)
    if not vineyard:
        raise HTTPException(status_code=404, detail="Vineyard not found")
    sort_mus(vineyard=vineyard)
    return vineyard


def get_vineyard_by_name(session: Session, name: str):
    statement = select(Vineyard).where(func.lower(Vineyard.name) == name.lower())
    vineyard = session.exec(statement).one_or_none()
    if not vineyard:
        raise HTTPException(status_code=404, detail="Vineyard not found")
    return vineyard


def eagerly_get_vineyard_managment_units_by_id(session: Session, vineyard_id: int):
    management_units = session.exec(
        select(ManagementUnit)
        .where(ManagementUnit.vineyard_id == vineyard_id)
        .order_by(ManagementUnit.name)
        .options(
            selectinload(ManagementUnit.variety),
            selectinload(ManagementUnit.status),
        )
    ).all()
    return management_units


def get_all_management_units(session: Session):
    query = select(ManagementUnit).order_by(ManagementUnit.name)

    management_units = session.exec(query)
    if not management_units:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No management units found"
        )
    return management_units


def get_red_management_units(session: Session):
    statement = (
        select(ManagementUnit)
        .join(ManagementUnit.variety)  # join to Variety
        .join(Variety.wine_colour)  # join to WineColour
        .where(WineColour.name == "Red")
    )
    results = session.exec(statement).all()
    return results


def get_red_management_units(session: Session):
    statement = (
        select(ManagementUnit)
        .join(ManagementUnit.variety)  # join to Variety
        .join(Variety.wine_colour)  # join to WineColour
        .where(WineColour.name == "White")
    )
    results = session.exec(statement).all()
    return results


def eagerly_get_management_unit_by_id(session: Session, id: int):
    management_unit = session.exec(
        select(ManagementUnit)
        .where(ManagementUnit.id == id)
        .options(
            selectinload(ManagementUnit.variety),
            selectinload(ManagementUnit.status),
        )
    ).one_or_none()

    if not management_unit:
        raise HTTPException(status_code=404, detail="Management unit not found")

    return management_unit


def all_chemicals(session: Session):
    query = select(Chemical).order_by(Chemical.name)

    chemicals = session.exec(query)
    return chemicals


def all_varieties(session: Session):
    query = select(Variety).order_by(Variety.name)

    varieties = session.exec(query)
    return varieties


def all_growth_stages(session: Session):
    query = select(GrowthStage).order_by(GrowthStage.el_number)

    varieties = session.exec(query).all()
    return varieties


def get_all_spray_records(session: Session):
    statement = (
        select(SprayRecord)
        .join(Spray.growth_stage)
        .options(
            selectinload(SprayRecord.spray).selectinload(Spray.growth_stage),
        )
        .order_by(asc(GrowthStage.el_number))
    )

    spray_records = session.exec(statement).all()
    return spray_records


# TODO Reduce eagerness!
def eagerly_get_vineyard_spray_records(
    session: Session, vineyard_id: int
) -> list[SprayRecord]:
    statement = (
        select(SprayRecord)
        .join(SprayRecord.management_unit)
        .join(SprayRecord.spray)
        .join(Spray.growth_stage)  # for ordering
        .where(ManagementUnit.vineyard_id == vineyard_id)
        .options(
            selectinload(SprayRecord.management_unit)
            .selectinload(ManagementUnit.variety)
            .selectinload(Variety.wine_colour),
            selectinload(SprayRecord.spray).selectinload(Spray.growth_stage),
            selectinload(SprayRecord.spray)
            .selectinload(Spray.spray_chemicals)
            .selectinload(SprayChemical.chemical)
            .selectinload(Chemical.chemical_groups),
        )
        .order_by(asc(GrowthStage.el_number))
    )
    spray_records = session.exec(statement).all()
    # Sort by el_number - # NOTE maybe else should be 0 if no growth stage to put to top of list?
    spray_records.sort(
        key=lambda sr: sr.spray.growth_stage.el_number if sr.spray.growth_stage else 999
    )
    return spray_records


def eagerly_get_spray_record_by_id(
    session: Session, spray_record_id: int
) -> SprayRecord | None:
    statement = (
        select(SprayRecord)
        .where(SprayRecord.id == spray_record_id)
        .options(
            joinedload(SprayRecord.management_unit)
            .joinedload(ManagementUnit.variety)
            .joinedload(Variety.wine_colour),
            joinedload(SprayRecord.spray),
            joinedload(SprayRecord.growth_stage),
            joinedload(SprayRecord.spray_record_chemicals).joinedload(
                SprayRecordChemical.chemical
            ),
        )
    )
    spray_record = session.exec(statement).first()
    ic(spray_record)
    return spray_record


def eagerly_get_vineyard_spray_spray_records(
    session: Session, vineyard_id: int, spray_id: int
) -> list[SprayRecord]:
    statement = (
        select(SprayRecord)
        .join(SprayRecord.management_unit)
        .join(SprayRecord.spray)
        .where(ManagementUnit.vineyard_id == vineyard_id)
        .where(SprayRecord.spray_id == spray_id)
        .options(
            selectinload(SprayRecord.management_unit)
            .selectinload(ManagementUnit.variety)
            .selectinload(Variety.wine_colour),
            selectinload(SprayRecord.spray).selectinload(Spray.growth_stage),
            selectinload(SprayRecord.spray)
            .selectinload(Spray.spray_chemicals)
            .selectinload(SprayChemical.chemical)
            .selectinload(Chemical.chemical_groups),
        )
        .order_by(asc(ManagementUnit.name))
    )
    spray_records = session.exec(statement).all()
    spray_records.sort(key=lambda sr: sr.management_unit.name or "")
    ic(spray_records)
    return spray_records


# TODO Reduce eagerness!
def eagerly_get_vineyard_sprays(session: Session, vineyard_id: int) -> list[Spray]:
    statement = (
        select(Spray)
        .distinct(Spray.id)
        .join(Spray.spray_records)
        .join(SprayRecord.management_unit)
        .join(Spray.growth_stage)
        .where(ManagementUnit.vineyard_id == vineyard_id)
        .options(
            selectinload(Spray.growth_stage),
            selectinload(Spray.spray_chemicals)
            .selectinload(SprayChemical.chemical)
            .selectinload(Chemical.chemical_groups),
            selectinload(Spray.spray_records)
            .selectinload(SprayRecord.management_unit)
            .selectinload(ManagementUnit.variety)
            .selectinload(Variety.wine_colour),
        )
        .order_by(Spray.id, GrowthStage.el_number)
    )
    sprays = session.exec(statement).all()
    # Sort by el_number - # NOTE maybe else should be 0 if no growth stage to put to top of list?
    sprays.sort(key=lambda sp: sp.growth_stage.el_number if sp.growth_stage else 999)
    return sprays


def get_spray_chemicals(spray_id: int, session: Session) -> list[Chemical]:
    statement = (
        select(Chemical).join(SprayChemical).filter(SprayChemical.spray_id == spray_id)
    )
    spray_chemicals = session.exec(statement).all()
    return spray_chemicals


def get_spray_record_chemicals(
    spray_record_id: int, session: Session
) -> list[Chemical]:
    statement = (
        select(Chemical)
        .join(SprayRecordChemical)
        .filter(SprayRecordChemical.spray_record_id == spray_record_id)
    )
    spray_record_chemicals = session.exec(statement).all()
    return spray_record_chemicals


def spray_complete_for_vineyard(
    session: Session, spray_id: int, vineyard_id: int
) -> bool:
    """
    Check if a spray program is complete for all management units that have spray records for this program.
    Returns True if all spray records for this program in this vineyard are marked as complete.
    Returns False if there are no spray records for this program, or if any are incomplete.
    """
    from sqlmodel import select

    # Get all spray records for this spray program in this vineyard
    statement = (
        select(SprayRecord)
        .join(ManagementUnit)
        .where(
            SprayRecord.spray_id == spray_id,
            ManagementUnit.vineyard_id == vineyard_id,
        )
    )
    spray_records = session.exec(statement).all()

    # If no spray records exist for this program, consider it incomplete
    if not spray_records:
        return False

    # Check if all spray records are complete
    return all(record.complete for record in spray_records)
