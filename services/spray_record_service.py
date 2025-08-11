import datetime

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


def update_multiple_spray_records(
    session,
    spray_id,
    management_unit_ids,
    operator_id,
    growth_stage_id,
    hours_taken,
    temperature,
    relative_humidity,
    wind_speed,
    wind_direction,
    chem_batch_map,
):
    for mu_id in management_unit_ids:
        spray_record = session.exec(
            select(SprayRecord).where(
                SprayRecord.management_unit_id == int(mu_id),
                SprayRecord.spray_id == spray_id,
            )
        ).first()
        if not spray_record:
            continue

        spray_record.operator_id = operator_id
        spray_record.growth_stage_id = growth_stage_id
        spray_record.hours_taken = hours_taken
        spray_record.temperature = temperature
        spray_record.relative_humidity = relative_humidity
        spray_record.wind_speed = wind_speed
        spray_record.wind_direction = wind_direction
        spray_record.complete = True
        spray_record.date_completed = datetime.datetime.now()

        for chem_id, batch_number in chem_batch_map.items():
            existing = session.exec(
                select(SprayRecordChemical).where(
                    SprayRecordChemical.spray_record_id == spray_record.id,
                    SprayRecordChemical.chemical_id == chem_id,
                )
            ).first()
            if existing:
                existing.batch_number = batch_number
                src = existing
            else:
                src = SprayRecordChemical(
                    spray_record_id=spray_record.id,
                    chemical_id=chem_id,
                    batch_number=batch_number,
                )
            session.add(src)

        session.add(spray_record)
    session.commit()
