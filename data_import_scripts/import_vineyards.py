import pandas as pd
from sqlmodel import Session, select

import database
from data.vineyard import Vineyard

# Run as module from root dir:  python -m data_import_scripts.import_vineyards


def import_vineyards(csv_path: str):
    df = pd.read_csv(csv_path)

    # Normalize names: strip whitespace, drop empty, remove duplicates
    df["Vineyard Name"] = df["Vineyard Name"].str.strip()
    df = df[df["Vineyard Name"].notnull()]
    df = df.drop_duplicates(subset=["Vineyard Name"])

    with Session(database.engine) as session:
        # Get existing vineyard names from DB

        results = session.exec(select(Vineyard.name)).all()
        existing_names = set(results)

        # Filter new names only
        new_vineyards = []
        for _, row in df.iterrows():
            name = row["Vineyard Name"]
            if name not in existing_names:
                new_vineyards.append(Vineyard(name=name))

        # Insert only new vineyards
        if new_vineyards:
            session.add_all(new_vineyards)
            session.commit()
            print(f"✅ Imported {len(new_vineyards)} new vineyard(s).")
        else:
            print("ℹ️ No new vineyards to import.")


if __name__ == "__main__":
    import_vineyards("data_import_scripts/vineyards.csv")
