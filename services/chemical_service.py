# services/chemical_service.py

from typing import List, Optional

from sqlmodel import Session, select

from data.vineyard import Chemical, ChemicalGroup, MixRateUnit


def get_chemical_by_id(session: Session, chemical_id: int) -> Optional[Chemical]:
    """Get a chemical by ID"""
    return session.get(Chemical, chemical_id)


def get_chemical_by_name(session: Session, name: str) -> Optional[Chemical]:
    """Get a chemical by name"""
    return session.exec(select(Chemical).where(Chemical.name == name)).first()


def get_all_chemicals(session: Session) -> List[Chemical]:
    """Get all chemicals"""
    return session.exec(select(Chemical)).all()


def get_chemicals_by_group(session: Session, group_id: int) -> List[Chemical]:
    """Get chemicals by chemical group"""
    group = session.get(ChemicalGroup, group_id)
    if group:
        return group.chemicals or []
    return []


def create_chemical(
    session: Session,
    name: str,
    active_ingredient: str,
    rate_per_100l: Optional[int] = None,
    rate_unit: str = MixRateUnit.MILLILITRES.value,
    chemical_group_ids: List[int] = None,
) -> Optional[Chemical]:
    """Create a new chemical"""
    try:
        # Convert rate_unit string to enum
        rate_unit_enum = (
            MixRateUnit(rate_unit) if rate_unit else MixRateUnit.MILLILITRES
        )

        chemical = Chemical(
            name=name.strip(),
            active_ingredient=active_ingredient.strip(),
            rate_per_100l=rate_per_100l,
            rate_unit=rate_unit_enum,
        )

        session.add(chemical)
        session.flush()  # Flush to get the ID

        # Add chemical groups if provided
        if chemical_group_ids:
            for group_id in chemical_group_ids:
                group = session.get(ChemicalGroup, group_id)
                if group:
                    if not chemical.chemical_groups:
                        chemical.chemical_groups = []
                    chemical.chemical_groups.append(group)

        session.commit()
        session.refresh(chemical)
        return chemical

    except Exception as e:
        session.rollback()
        print(f"Error creating chemical: {e}")
        return None


def update_chemical(
    session: Session,
    chemical_id: int,
    name: str,
    active_ingredient: str,
    rate_per_100l: Optional[int] = None,
    rate_unit: str = MixRateUnit.MILLILITRES.value,
    chemical_group_ids: List[int] = None,
) -> Optional[Chemical]:
    """Update an existing chemical"""
    try:
        chemical = session.get(Chemical, chemical_id)
        if not chemical:
            return None

        # Convert rate_unit string to enum
        rate_unit_enum = (
            MixRateUnit(rate_unit) if rate_unit else MixRateUnit.MILLILITRES
        )

        # Update basic fields
        chemical.name = name.strip()
        chemical.active_ingredient = active_ingredient.strip()
        chemical.rate_per_100l = rate_per_100l
        chemical.rate_unit = rate_unit_enum

        # Update chemical groups
        # First, clear existing groups
        if chemical.chemical_groups:
            chemical.chemical_groups.clear()

        # Add new groups if provided
        if chemical_group_ids:
            for group_id in chemical_group_ids:
                group = session.get(ChemicalGroup, group_id)
                if group:
                    if not chemical.chemical_groups:
                        chemical.chemical_groups = []
                    chemical.chemical_groups.append(group)

        session.commit()
        session.refresh(chemical)
        return chemical

    except Exception as e:
        session.rollback()
        print(f"Error updating chemical: {e}")
        return None


def delete_chemical(session: Session, chemical_id: int) -> bool:
    """Delete a chemical"""
    try:
        chemical = session.get(Chemical, chemical_id)
        if not chemical:
            return False

        session.delete(chemical)
        session.commit()
        return True

    except Exception as e:
        session.rollback()
        print(f"Error deleting chemical: {e}")
        return False
