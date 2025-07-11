from fastapi import HTTPException, status
from icecream import ic
from sqlalchemy import asc, func
from sqlalchemy.orm import joinedload, selectinload
from sqlmodel import Session, select

from data.vineyard import (
    Chemical,
    GrowthStage,
    ManagementUnit,
    SprayProgram,
    SprayProgramChemical,
    SprayRecord,
    SprayRecordChemical,
    Variety,
    Vineyard,
    WineColour,
)


def all_vineyards(session: Session):
    query = select(Vineyard).order_by(Vineyard.name)

    vineyards = session.exec(query)
    return vineyards


def get_vineyard_by_id(session: Session, id: int):
    print("GETTING VINEYARD BY ID")
    vineyard = session.get(Vineyard, id)
    if not vineyard:
        raise HTTPException(status_code=404, detail="Vineyard not found")
    return vineyard


def get_vineyard_by_name(session: Session, name: str):
    statement = select(Vineyard).where(func.lower(Vineyard.name) == name.lower())
    vineyard = session.exec(statement).one_or_none()
    if not vineyard:
        raise HTTPException(status_code=404, detail="Vineyard not found")
    return vineyard


def eagerly_get_vineyard_managment_units_by_id(session: Session, id: int):
    management_units = session.exec(
        select(ManagementUnit)
        .where(ManagementUnit.vineyard_id == id)
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


# TODO Reduce eagerness!
def eagerly_get_vineyard_spray_records(
    session: Session, vineyard_id: int
) -> list[SprayRecord]:
    statement = (
        select(SprayRecord)
        .join(SprayRecord.management_unit)
        .join(SprayRecord.spray_program)
        .join(SprayProgram.growth_stage)  # for ordering
        .where(ManagementUnit.vineyard_id == vineyard_id)
        .options(
            selectinload(SprayRecord.management_unit)
            .selectinload(ManagementUnit.variety)
            .selectinload(Variety.wine_colour),
            selectinload(SprayRecord.spray_program).selectinload(
                SprayProgram.growth_stage
            ),
            selectinload(SprayRecord.spray_program)
            .selectinload(SprayProgram.spray_program_chemicals)
            .selectinload(SprayProgramChemical.chemical)
            .selectinload(Chemical.chemical_groups),
        )
        .order_by(asc(GrowthStage.el_number))
    )
    spray_records = session.exec(statement).all()
    # Sort by el_number - # NOTE maybe else should be 0 if no growth stage to put to top of list?
    spray_records.sort(
        key=lambda sr: sr.spray_program.growth_stage.el_number
        if sr.spray_program.growth_stage
        else 999
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
            joinedload(SprayRecord.spray_program),
            joinedload(SprayRecord.growth_stage),
            joinedload(SprayRecord.spray_record_chemicals).joinedload(
                SprayRecordChemical.chemical
            ),
        )
    )
    spray_record = session.exec(statement).first()
    ic(spray_record)
    return spray_record


def eagerly_get_vineyard_spray_program_spray_records(
    session: Session, vineyard_id: int, spray_program_id: int
) -> list[SprayRecord]:
    statement = (
        select(SprayRecord)
        .join(SprayRecord.management_unit)
        .join(SprayRecord.spray_program)
        .where(ManagementUnit.vineyard_id == vineyard_id)
        .where(SprayRecord.spray_program_id == spray_program_id)
        .options(
            selectinload(SprayRecord.management_unit)
            .selectinload(ManagementUnit.variety)
            .selectinload(Variety.wine_colour),
            selectinload(SprayRecord.spray_program).selectinload(
                SprayProgram.growth_stage
            ),
            selectinload(SprayRecord.spray_program)
            .selectinload(SprayProgram.spray_program_chemicals)
            .selectinload(SprayProgramChemical.chemical)
            .selectinload(Chemical.chemical_groups),
        )
        .order_by(asc(ManagementUnit.name))
    )
    spray_records = session.exec(statement).all()
    spray_records.sort(key=lambda sr: sr.management_unit.name or "")
    ic(spray_records)
    return spray_records


# TODO Reduce eagerness!
def eagerly_get_vineyard_spray_programs(
    session: Session, vineyard_id: int
) -> list[SprayProgram]:
    statement = (
        select(SprayProgram)
        .distinct(SprayProgram.id)
        .join(SprayProgram.spray_records)
        .join(SprayRecord.management_unit)
        .join(SprayProgram.growth_stage)
        .where(ManagementUnit.vineyard_id == vineyard_id)
        .options(
            selectinload(SprayProgram.growth_stage),
            selectinload(SprayProgram.spray_program_chemicals)
            .selectinload(SprayProgramChemical.chemical)
            .selectinload(Chemical.chemical_groups),
            selectinload(SprayProgram.spray_records)
            .selectinload(SprayRecord.management_unit)
            .selectinload(ManagementUnit.variety)
            .selectinload(Variety.wine_colour),
        )
        .order_by(SprayProgram.id, GrowthStage.el_number)
    )
    spray_programs = session.exec(statement).all()
    # Sort by el_number - # NOTE maybe else should be 0 if no growth stage to put to top of list?
    spray_programs.sort(
        key=lambda sp: sp.growth_stage.el_number if sp.growth_stage else 999
    )
    return spray_programs


def get_spray_program_chemicals(
    spray_program_id: int, session: Session
) -> list[Chemical]:
    statement = (
        select(Chemical)
        .join(SprayProgramChemical)
        .filter(SprayProgramChemical.spray_program_id == spray_program_id)
    )
    spray_program_chemicals = session.exec(statement).all()
    return spray_program_chemicals


def spray_program_complete_for_vineyard(
    session: Session, spray_program_id: int, vineyard_id: int
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
            SprayRecord.spray_program_id == spray_program_id,
            ManagementUnit.vineyard_id == vineyard_id,
        )
    )
    spray_records = session.exec(statement).all()

    # If no spray records exist for this program, consider it incomplete
    if not spray_records:
        return False

    # Check if all spray records are complete
    return all(record.complete for record in spray_records)
