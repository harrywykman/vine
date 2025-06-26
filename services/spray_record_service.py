from sqlmodel import Session, select

from data.vineyard import SprayRecord


def create_or_update_spray_record(
    session: Session, mu_id: int, sp_id: int
) -> SprayRecord:
    # Check for an existing record
    statement = select(SprayRecord).where(
        SprayRecord.management_unit_id == mu_id, SprayRecord.spray_program_id == sp_id
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
            spray_program_id=sp_id,
        )
        session.add(spray_record)

    session.commit()
    session.refresh(spray_record)  # Optional: refresh from DB to ensure up-to-date
    return spray_record
