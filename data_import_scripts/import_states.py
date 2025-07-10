# insert_states.py

from sqlmodel import Session, select

from data.vineyard import Status
from database import engine

# The data to insert or update
states_data = [
    {"id": 1, "status": "Active"},
    {"id": 2, "status": "Fallow"},
]


def insert_or_update_states():
    with Session(engine) as session:
        for entry in states_data:
            existing = session.exec(
                select(Status).where(Status.id == entry["id"])
            ).first()

            if existing:
                print(f"Updating status ID {entry['id']} -> {entry['status']}")
                existing.status = entry["status"]
                session.add(existing)
            else:
                print(f"Inserting status ID {entry['id']} -> {entry['status']}")
                new_status = Status(id=entry["id"], status=entry["status"])
                session.add(new_status)

        session.commit()
        print("Insert/update complete.")


if __name__ == "__main__":
    insert_or_update_states()
