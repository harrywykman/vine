import csv

from sqlmodel import Session, select

from data.vineyard import Chemical
from dependencies import get_session

# CSV_FILE_PATH = "./data_import_scripts/chemicals.csv"  # or an absolute path


def load_chemicals_from_csv(file_path: str) -> list[dict[str, str]]:
    with open(file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        chemicals = [
            {
                "name": row["name"].strip(),
                "active_ingredient": row["active_ingredient"].strip(),
            }
            for row in reader
            if row["name"].strip() and row["active_ingredient"].strip()
        ]
    return chemicals


def import_chemicals(file_path: str):
    chemicals = load_chemicals_from_csv(file_path)
    session_generator = get_session()
    session: Session = next(session_generator)
    try:
        added_count = 0
        for chem in chemicals:
            # Check for existing entry
            statement = select(Chemical).where(
                Chemical.name == chem["name"],
                Chemical.active_ingredient == chem["active_ingredient"],
            )
            result = session.exec(statement).first()

            if result is None:
                new_chem = Chemical(
                    name=chem["name"], active_ingredient=chem["active_ingredient"]
                )
                session.add(new_chem)
                added_count += 1

        session.commit()
        print(f"✅ Imported {added_count} new chemicals.")
    except Exception as e:
        session.rollback()
        print(f"❌ Error importing chemicals: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    import_chemicals("./data_import_scripts/chemicals.csv")
