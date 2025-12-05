from decimal import Decimal, InvalidOperation
from typing import Optional

import fastapi_chameleon
from fastapi import HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select
from starlette import status

from data.vineyard import (
    Chemical,
    GrowthStage,
    Spray,
    SprayChemical,
    SprayProgram,
    Target,
)


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
    spray_program_id: int,  # Now required, not optional
    concentration_factors: Optional[list] = None,  # Added for completeness
) -> Spray:
    # Validation
    if not name:
        raise ValueError("Name is required")
    if not water_spray_rate_per_hectare:
        raise ValueError("Water spray rate is required")
    if not growth_stage_id:
        raise ValueError("A growth stage is required")
    if not spray_program_id:
        raise ValueError("Spray program ID is required")

    # Verify spray program exists
    spray_program = session.get(SprayProgram, spray_program_id)
    if not spray_program:
        raise ValueError(f"Spray program with ID {spray_program_id} not found")

    # Verify growth stage exists
    growth_stage = session.get(GrowthStage, growth_stage_id)
    if not growth_stage:
        raise ValueError(f"Growth stage with ID {growth_stage_id} not found")

    # Create spray with direct foreign key relationship
    spray = Spray(
        name=name,
        water_spray_rate_per_hectare=water_spray_rate_per_hectare,
        growth_stage_id=growth_stage_id,
        spray_program_id=spray_program_id,  # Direct assignment
    )

    session.add(spray)
    session.flush()  # Get ID before adding chemicals

    # Add associated chemicals
    for chem_id, target, concentration_factor in chemicals_targets:
        if not chem_id or not target:
            continue  # Skip empty rows

        # Convert concentration_factor to Decimal
        try:
            concentration_factor = Decimal(str(concentration_factor))
        except (ValueError, TypeError, InvalidOperation):
            concentration_factor = Decimal("1.0")

        # Verify chemical exists
        chemical = session.get(Chemical, int(chem_id))
        if not chemical:
            raise ValueError(f"Chemical with ID {chem_id} not found")

        # Convert target to enum
        try:
            target_enum = Target(target) if target else None
        except ValueError:
            raise ValueError(f"Invalid target value: {target}")

        spray_chemical = SprayChemical(
            spray_id=spray.id,
            chemical_id=int(chem_id),
            target=target_enum,
            concentration_factor=concentration_factor,
        )
        session.add(spray_chemical)

    session.commit()
    return spray


def delete_spray(session: Session, id: int):
    spray = eagerly_get_spray_by_id(id, session)

    print(spray)

    if not spray:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Spray not found"
        )

    try:
        session.delete(spray)
        session.commit()
    except Exception:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete spray",
        )
