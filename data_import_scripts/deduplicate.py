# deduplicate.py

from sqlalchemy import func, select
from sqlmodel import Session

from data.vineyard import SprayRecordChemical  # adjust as needed
from database import engine


def deduplicate_spray_record_chemicals(session: Session):
    # Step 1: Find duplicate spray_record_id + chemical_id combos
    duplicates = session.exec(
        select(
            SprayRecordChemical.spray_record_id,
            SprayRecordChemical.chemical_id,
            func.count(SprayRecordChemical.id).label("count"),
        )
        .group_by(SprayRecordChemical.spray_record_id, SprayRecordChemical.chemical_id)
        .having(func.count(SprayRecordChemical.id) > 1)
    ).all()

    print(f"Found {len(duplicates)} duplicate (spray_record_id, chemical_id) pairs.")

    # Step 2: For each duplicate set, keep one and delete others
    total_deleted = 0
    for spray_record_id, chemical_id, _ in duplicates:
        dupes = (
            session.exec(
                select(SprayRecordChemical)
                .where(
                    SprayRecordChemical.spray_record_id == spray_record_id,
                    SprayRecordChemical.chemical_id == chemical_id,
                )
                .order_by(SprayRecordChemical.id)
            )
            .scalars()
            .all()
        )

        # Delete all but the first
        for dupe in dupes[1:]:
            session.delete(dupe)
            total_deleted += 1

    session.commit()
    print(f"Deleted {total_deleted} duplicate records.")


if __name__ == "__main__":
    with Session(engine) as session:
        deduplicate_spray_record_chemicals(session)
        print("Duplicates removed.")
