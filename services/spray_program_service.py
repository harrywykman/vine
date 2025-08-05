from typing import List, Optional

from sqlalchemy import desc
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from data.vineyard import GrowthStage, Spray, SprayProgram


def get_all_spray_programs(session: Session) -> List[SprayProgram]:
    statement = select(SprayProgram).order_by(desc(SprayProgram.year_start))
    spray_programs = session.exec(statement).all()
    return spray_programs


def get_spray_program_by_id(session: Session, spray_program_id: int) -> SprayProgram:
    statement = select(SprayProgram).where(SprayProgram.id == spray_program_id)
    spray_program = session.exec(statement).one_or_none()
    if not spray_program:
        raise ValueError(f"Spray program with ID {spray_program_id} not found")
    return spray_program


def get_sprays_by_program_id(session: Session, spray_program_id: int) -> List[Spray]:
    statement = (
        select(Spray)
        .join(SprayProgramSprayLink)
        .where(SprayProgramSprayLink.spray_program_id == spray_program_id)
        .options(selectinload(Spray.growth_stage))
    )

    sprays = session.exec(statement).all()
    return sprays


""" def eagerly_get_all_spray_program_sprays(
    session: Session, spray_program_id: int
) -> List[Spray]:
    statement = (
        select(SprayProgram)
        .where(SprayProgram.id == spray_program_id)
        .options(selectinload(SprayProgram.sprays).selectinload(Spray.growth_stage))
    )

    spray_program = session.exec(statement).one_or_none()

    if not spray_program:
        raise ValueError(f"Spray program with ID {spray_program_id} not found")

    return sorted(
        spray_program.sprays,
        key=lambda spray: spray.growth_stage.el_number
        if spray.growth_stage
        else float("inf"),
    ) """


def eagerly_get_all_spray_program_sprays(
    session: Session, spray_program_id: int
) -> List[Spray]:
    statement = (
        select(Spray)
        .where(Spray.spray_program_id == spray_program_id)
        .join(GrowthStage, isouter=True)  # Left join in case growth_stage is None
        .order_by(GrowthStage.el_number.nulls_last())
        .options(selectinload(Spray.growth_stage))
    )
    sprays = session.exec(statement).all()

    # Verify spray program exists
    spray_program_exists = session.exec(
        select(SprayProgram).where(SprayProgram.id == spray_program_id)
    ).one_or_none()

    if not spray_program_exists:
        raise ValueError(f"Spray program with ID {spray_program_id} not found")

    return sprays


def create_spray_program(
    session: Session,
    name: Optional[str],
    year_start: int,
    year_end: int,
) -> SprayProgram:
    if not name:
        raise Exception("name is required")
    if not year_start:
        raise Exception("year_start is required")
    if not year_end:
        raise Exception("year_end is required")

    spray_program = SprayProgram()
    spray_program.name = name
    spray_program.year_start = year_start
    spray_program.year_end = year_end

    session.add(spray_program)
    session.flush()  # Get ID before commit

    session.commit()

    return spray_program
