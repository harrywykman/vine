# export_chemicals.py

import json

from sqlmodel import Session, select

from data.vineyard import Chemical
from database import engine


def export_chemicals_to_json(file_path="./data_import_scripts/chemicals_export.json"):
    with Session(engine) as session:
        chemicals = session.exec(select(Chemical)).all()

        export_data = []
        for chem in chemicals:
            chem_dict = {
                "name": chem.name,
                "active_ingredient": chem.active_ingredient,
                "rate_per_100l": chem.rate_per_100l,
                "rate_unit": chem.rate_unit.value if chem.rate_unit else None,
                "chemical_groups": [group.code for group in chem.chemical_groups or []],
            }
            export_data.append(chem_dict)

        with open(file_path, "w") as f:
            json.dump(export_data, f, indent=2)

        print(f"Exported {len(export_data)} chemicals to {file_path}")


if __name__ == "__main__":
    export_chemicals_to_json()
