from decimal import Decimal
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select
from starlette import status

from data.vineyard import SprayProgram, SprayProgramChemical


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


def create_spray_program(
    session: Session,
    name: Optional[str],
    water_spray_rate_per_hectare: Optional[Decimal],
    chemicals_mix_rates: list,
) -> SprayProgram:
    if not name:
        raise Exception("password is required")
    if not water_spray_rate_per_hectare:
        raise Exception("spray rate is required")

    spray_program = SprayProgram()
    spray_program.name = name
    spray_program.water_spray_rate_per_hectare = water_spray_rate_per_hectare

    session.add(spray_program)
    session.flush()  # Get ID before commit

    # Add associated chemicals
    for chem_id, rate in chemicals_mix_rates:
        if not chem_id or not rate:
            continue  # Skip empty rows
        spc = SprayProgramChemical(
            spray_program_id=spray_program.id,
            chemical_id=int(chem_id),
            mix_rate_per_100L=Decimal(rate),
        )
        session.add(spc)

    session.commit()

    return spray_program


def delete_spray_program(session: Session, id: int):
    spray_program = session.query(SprayProgram).get(id)

    if not spray_program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Spray Program not found"
        )

    try:
        session.delete(spray_program)
        session.commit()
    except Exception:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete spray program",
        )
