from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from data.vineyard import (
    Chemical,
    ManagementUnit,
    SprayProgram,
    SprayProgramChemical,
    Variety,
    Vineyard,
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


def eagerly_get_all_spray_programs(session: Session):
    statement = select(SprayProgram).options(
        selectinload(SprayProgram.spray_program_chemicals).selectinload(
            SprayProgramChemical.chemical
        )
    )

    spray_programs = session.exec(statement)
    if not spray_programs:
        raise HTTPException(status_code=404, detail="No Spray Programs Found")
    return spray_programs
