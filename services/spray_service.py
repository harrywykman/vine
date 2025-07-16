from decimal import Decimal
from typing import Optional

import fastapi_chameleon
from fastapi import HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select
from starlette import status

from data.vineyard import GrowthStage, Spray, SprayChemical


def eagerly_get_all_sprays(session: Session) -> list[Spray]:
    statement = (
        select(Spray)
        .join(Spray.growth_stage)
        .options(
            selectinload(Spray.growth_stage),
            selectinload(Spray.spray_chemicals).selectinload(SprayChemical.chemical),
        )
        .order_by(GrowthStage.el_number)
    )
    sprays = session.exec(statement).all()
    return sprays


def eagerly_get_spray_by_id(id: int, session: Session) -> Spray:
    statement = (
        select(Spray)
        .where(Spray.id == id)
        .options(
            selectinload(Spray.spray_chemicals).selectinload(SprayChemical.chemical)
        )
    )

    spray = session.exec(statement).first()
    if not spray:
        fastapi_chameleon.not_found()
    return spray


def create_spray(
    session: Session,
    name: Optional[str],
    water_spray_rate_per_hectare: Optional[Decimal],
    chemicals_targets: list,
    growth_stage_id: int,
) -> Spray:
    if not name:
        raise Exception("name is required")
    if not water_spray_rate_per_hectare:
        raise Exception("spray rate is required")
    if not growth_stage_id:
        raise Exception("A growth rate is required")

    spray = Spray()
    spray.name = name
    spray.water_spray_rate_per_hectare = water_spray_rate_per_hectare
    spray.growth_stage_id = growth_stage_id  # check if growth stage exists

    session.add(spray)
    session.flush()  # Get ID before commit

    # Add associated chemicals
    for chem_id, target in chemicals_targets:
        if not chem_id or not target:
            continue  # Skip empty rows
        spc = SprayChemical(
            spray_id=spray.id,
            chemical_id=int(chem_id),
            target=str(target),
        )
        session.add(spc)

    session.commit()

    return spray


def delete_spray(session: Session, id: int):
    spray = eagerly_get_spray_by_id(id, session)

    print(spray)

    if not spray:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Spray Program not found"
        )

    try:
        session.delete(spray)
        session.commit()
    except Exception:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete spray program",
        )
