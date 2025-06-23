import pandas as pd
from sqlalchemy.dialects.postgresql import insert
from sqlmodel import Session, select

import database  # Your database engine
from data.vineyard import Variety, WineColour


def import_varieties(csv_path: str):
    df = pd.read_csv(csv_path, usecols=["Variety Name", "WineColour"])
    df = df.dropna().copy()

    # Normalize strings
    df["Variety Name"] = df["Variety Name"].str.strip()
    df["WineColour"] = df["WineColour"].str.strip().str.capitalize()

    df = df.drop_duplicates()

    with Session(database.engine) as session:
        # Load existing variety names (lowercased)
        existing_varieties = set()
        try:
            rows = session.exec(select(Variety.name)).all()
            for row in rows:
                name = row[0]  # row is a tuple like (name,)
                if name is None:
                    continue
                existing_varieties.add(name.lower())
        except Exception as e:
            print("Error loading existing varieties:", e)
            raise

        # Load existing WineColour objects into a dict keyed by lowercase name
        wine_colour_map = {
            wc.name.lower(): wc for wc in session.exec(select(WineColour)).all()
        }

        new_varieties = []
        new_colours = []

        for _, row in df.iterrows():
            var_name = row["Variety Name"]
            colour_name = row["WineColour"]
            var_name_lower = var_name.lower()
            colour_name_lower = colour_name.lower()

            if var_name_lower in existing_varieties:
                # Skip duplicates
                continue

            # Ensure WineColour exists or create new
            wc = wine_colour_map.get(colour_name_lower)
            if not wc:
                wc = WineColour(name=colour_name)
                session.add(wc)
                session.flush()  # flush to assign wc.id
                wine_colour_map[colour_name_lower] = wc

            new_varieties.append({"name": var_name, "wine_colour_id": wc.id})
            existing_varieties.add(var_name_lower)

        if new_varieties:
            # Use insert with ON CONFLICT DO NOTHING to avoid duplicates if race condition
            stmt = insert(Variety).values(new_varieties)
            stmt = stmt.on_conflict_do_nothing(index_elements=["name"])

            session.exec(stmt)
            session.commit()
            print(f"✅ Imported {len(new_varieties)} Variety entries.")
        else:
            print("ℹ️ No new Variety entries to import.")


if __name__ == "__main__":
    import_varieties("data_import_scripts/varieties.csv")


""" import pandas as pd
from sqlmodel import Session, select

import database  # Your database engine definition
from data.vineyard import Variety, WineColour  # Adjust this import for your project


def import_varieties(csv_path: str):
    df = pd.read_csv(csv_path, usecols=["Variety Name", "WineColour"])
    df = df.dropna().copy()

    # Normalize strings
    df["Variety Name"] = df["Variety Name"].str.strip()
    df["WineColour"] = df["WineColour"].str.strip().str.capitalize()

    df = df.drop_duplicates()

    with Session(database.engine) as session:
        # Load existing records
        existing_varieties = set()
        try:
            rows = session.exec(select(Variety.name)).all()
            for row in rows:
                name = row[0]  # row is a tuple like (name,)
                if name is None:
                    continue
                existing_varieties.add(name.lower())
        except Exception as e:
            print("Error loading existing varieties:", e)
            raise

        wine_colour_map = {
            wc.name.lower(): wc for wc in session.exec(select(WineColour)).all()
        }

        new_varieties = []

        for _, row in df.iterrows():
            var_name = row["Variety Name"]
            colour_name = row["WineColour"]

            if var_name.lower() in existing_varieties:
                continue

            wc = wine_colour_map.get(colour_name.lower())
            if not wc:
                wc = WineColour(name=colour_name)
                session.add(wc)
                session.flush()
                wine_colour_map[colour_name.lower()] = wc

            new_varieties.append(Variety(name=var_name, wine_colour_id=wc.id))
            existing_varieties.add(var_name.lower())

        if new_varieties:
            session.add_all(new_varieties)
            session.commit()
            print(f"✅ Imported {len(new_varieties)} Variety entries.")
        else:
            print("ℹ️ No new Variety entries to import.")


if __name__ == "__main__":
    import_varieties("data_import_scripts/varieties.csv") """
