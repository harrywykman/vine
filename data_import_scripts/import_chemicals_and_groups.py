# import_chemicals.py

import json

from sqlmodel import Session, select

from data.vineyard import Chemical, ChemicalGroup, MixRateUnit
from database import engine  # Adjust this to your DB engine


def import_chemicals_from_json(file_path="./data_import_scripts/chemicals_export.json"):
    with open(file_path) as f:
        data = json.load(f)

    with Session(engine) as session:
        for entry in data:
            chem_name = entry["name"]

            # Check if the chemical already exists
            chemical = session.exec(
                select(Chemical).where(Chemical.name == chem_name)
            ).first()

            if chemical:
                print(f"Updating chemical: {chem_name}")
            else:
                print(f"Creating new chemical: {chem_name}")
                chemical = Chemical(name=chem_name)

            # Update fields
            chemical.active_ingredient = entry["active_ingredient"]
            chemical.rate_per_100l = entry["rate_per_100l"]
            chemical.rate_unit = (
                MixRateUnit(entry["rate_unit"]) if entry["rate_unit"] else None
            )

            # Resolve chemical group links
            group_codes = entry.get("chemical_groups", [])
            new_groups = []
            for code in group_codes:
                group = session.exec(
                    select(ChemicalGroup).where(ChemicalGroup.code == code)
                ).first()
                if group:
                    new_groups.append(group)
                else:
                    print(
                        f"Warning: ChemicalGroup with code '{code}' not found. Skipping."
                    )

            # Update relationships
            chemical.chemical_groups = new_groups

            # Add or update the chemical
            session.add(chemical)

        session.commit()
        print(f"Import complete. Processed {len(data)} chemicals.")


if __name__ == "__main__":
    import_chemicals_from_json("./data_import_scripts/chemicals_export.json")
