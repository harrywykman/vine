import fastapi_chameleon
from fastapi import HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from data.vineyard import ManagementUnit, SprayRecord, SprayRecordChemical, Variety


def get_spray_record_by_id(session: Session, id: int) -> SprayRecord:
    print("GETTING VINEYARD BY ID")
    spray_record = session.get(SprayRecord, id)
    if not spray_record:
        raise HTTPException(status_code=404, detail="Spray record not found")
    return spray_record


def eagerly_get_spray_record_by_id(id: int, session: Session) -> SprayRecord:
    statement = (
        select(SprayRecord)
        .where(SprayRecord.id == id)
        .options(
            selectinload(SprayRecord.spray_record_chemicals).selectinload(
                SprayRecordChemical.chemical
            ),
            selectinload(SprayRecord.management_unit)
            .selectinload(ManagementUnit.variety)
            .selectinload(Variety.wine_colour),
            selectinload(SprayRecord.growth_stage),
        )
    )

    spray_record = session.exec(statement).first()
    if not spray_record:
        fastapi_chameleon.not_found()
    return spray_record


def create_or_update_spray_record(
    session: Session, mu_id: int, sp_id: int
) -> SprayRecord:
    # Check for an existing record
    statement = select(SprayRecord).where(
        SprayRecord.management_unit_id == mu_id, SprayRecord.spray_id == sp_id
    )
    existing_record = session.exec(statement).first()

    if existing_record:
        # Update existing record
        # existing_record.operator = operator
        # Add other updates if needed
        session.add(existing_record)
        spray_record = existing_record
    else:
        # Create new record
        spray_record = SprayRecord(
            management_unit_id=mu_id,
            spray_id=sp_id,
        )
        session.add(spray_record)

    session.commit()
    session.refresh(spray_record)  # Optional: refresh from DB to ensure up-to-date
    return spray_record
