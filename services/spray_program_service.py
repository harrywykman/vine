from decimal import Decimal
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select
from starlette import status

from data.vineyard import GrowthStage, SprayProgram, SprayProgramChemical


def eagerly_get_all_spray_programs(session: Session) -> list[SprayProgram]:
    statement = (
        select(SprayProgram)
        .join(SprayProgram.growth_stage)
        .options(
            selectinload(SprayProgram.growth_stage),
            selectinload(SprayProgram.spray_program_chemicals).selectinload(
                SprayProgramChemical.chemical
            ),
        )
        .order_by(GrowthStage.el_number)
    )

    spray_programs = session.exec(statement).all()
    if not spray_programs:
        raise HTTPException(status_code=404, detail="No Spray Programs Found")
    return spray_programs


def eagerly_get_spray_program_by_id(id: int, session: Session) -> SprayProgram:
    statement = (
        select(SprayProgram)
        .where(SprayProgram.id == id)
        .options(
            selectinload(SprayProgram.spray_program_chemicals).selectinload(
                SprayProgramChemical.chemical
            )
        )
    )

    spray_program = session.exec(statement).first()
    if not spray_program:
        raise HTTPException(status_code=404, detail="Spray Program not found")

    return spray_program


def create_spray_program(
    session: Session,
    name: Optional[str],
    water_spray_rate_per_hectare: Optional[Decimal],
    chemicals_targets: list,
    growth_stage_id: int,
) -> SprayProgram:
    if not name:
        raise Exception("name is required")
    if not water_spray_rate_per_hectare:
        raise Exception("spray rate is required")
    if not growth_stage_id:
        raise Exception("A growth rate is required")

    spray_program = SprayProgram()
    spray_program.name = name
    spray_program.water_spray_rate_per_hectare = water_spray_rate_per_hectare
    spray_program.growth_stage_id = growth_stage_id  # check if growth stage exists

    session.add(spray_program)
    session.flush()  # Get ID before commit

    # Add associated chemicals
    for chem_id, target in chemicals_targets:
        if not chem_id or not target:
            continue  # Skip empty rows
        spc = SprayProgramChemical(
            spray_program_id=spray_program.id,
            chemical_id=int(chem_id),
            target=str(target),
        )
        session.add(spc)

    session.commit()

    return spray_program


def delete_spray_program(session: Session, id: int):
    spray_program = eagerly_get_spray_program_by_id(id, session)

    print(spray_program)

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
