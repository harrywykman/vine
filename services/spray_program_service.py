import datetime
from typing import List, Optional

from sqlalchemy import desc
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from data.vineyard import GrowthStage, Spray, SprayProgram, SpraySeason


def get_current_season(session: Session) -> Optional[SpraySeason]:
    return session.exec(
        select(SpraySeason).where(
            SpraySeason.is_current == True,
            SpraySeason.is_archived == False,
        )
    ).first()


def get_current_spray_programs(session: Session) -> List[SprayProgram]:
    season = get_current_season(session)
    if not season:
        return []
    return season.spray_programs


def get_all_spray_programs(session: Session) -> List[SprayProgram]:
    statement = (
        select(SprayProgram).join(SpraySeason).order_by(desc(SpraySeason.season_start))
    )
    spray_programs = session.exec(statement).all()
    return spray_programs


def get_programs_for_season(session: Session, season_id: int) -> List[SprayProgram]:
    season = session.get(SpraySeason, season_id)
    if not season:
        return []
    return season.spray_programs


def get_season_by_id(session: Session, season_id: int) -> Optional[SpraySeason]:
    return session.get(SpraySeason, season_id)


def get_all_seasons(session: Session) -> List[SpraySeason]:
    return session.exec(
        select(SpraySeason).order_by(desc(SpraySeason.season_start))
    ).all()


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
    spray_season_id: int,
) -> SprayProgram:
    if not name:
        raise Exception("name is required")

    if not spray_season_id:
        raise Exception("spray_season_id is required")

    spray_program = SprayProgram()
    spray_program.name = name
    spray_program.spray_season_id = spray_season_id

    session.add(spray_program)
    session.flush()

    session.commit()

    return spray_program


def archive_current_season_and_create_new(
    session: Session,
    new_season_name: str,
    new_season_start: datetime.date,
    new_season_end: datetime.date,
) -> SpraySeason:
    # Archive the current season
    current = get_current_season(session)
    if current:
        current.is_current = False
        current.is_archived = True
        session.add(current)

    # Create the new season
    new_season = SpraySeason(
        name=new_season_name,
        season_start=new_season_start,
        season_end=new_season_end,
        is_current=True,
        is_archived=False,
    )
    session.add(new_season)
    session.commit()
    session.refresh(new_season)
    return new_season
