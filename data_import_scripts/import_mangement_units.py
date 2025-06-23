from datetime import datetime
from decimal import Decimal

import pandas as pd
from sqlmodel import Session, select

import database
from data.vineyard import ManagementUnit, Status, Variety, Vineyard


def parse_rows_numbers(rows_numbers: str):
    # Parse strings like "1 to 16" into (1, 16)
    if not isinstance(rows_numbers, str) or "to" not in rows_numbers.lower():
        return None, None
    try:
        parts = rows_numbers.lower().split("to")
        start = int(parts[0].strip())
        end = int(parts[1].strip())
        return start, end
    except Exception:
        return None, None


def parse_plant_date(plant_date_str: str):
    # Extract first year from strings like "2020/2022" or parse date normally
    if not isinstance(plant_date_str, str):
        return None
    try:
        # Take first year if multiple years separated by slash
        year_part = plant_date_str.split("/")[0].strip()
        # Try to parse as year only
        year = int(year_part)
        return datetime(year, 1, 1).date()
    except Exception:
        try:
            return pd.to_datetime(plant_date_str).date()
        except Exception:
            return None


def import_management_units(csv_path: str):
    CSV_COLUMNS = [
        "Vineyard Name",
        "Variety Name",
        "WineColour",
        "Management Unit Area",
        "Management Unit Name",
        "Management Unit Rows Total",
        "Rows Numbers",
        "Management Unit Row Width",
        "Management Unit Vine Spacing",
        "VinesHa",
        "Total Vines",
        "Clone",
        "Source Vineyard",
        "Plant Date",
        "Status",
        "Management Unit Variety Name Modifier",
    ]

    df = pd.read_csv(csv_path, names=CSV_COLUMNS, header=0)

    # df = pd.read_csv(csv_path)

    # Normalize and trim strings for matching keys
    for col in ["Vineyard Name", "Variety Name", "Status", "Management Unit Name"]:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str).str.strip()

    # Drop rows missing required keys
    required_cols = [
        "Management Unit Name",
        "Variety Name",
        "Vineyard Name",
        # "Status",
        # "Management Unit Area",
        # "Management Unit Row Width",
        # "Management Unit Vine Spacing",
        # "Plant Date",
    ]
    df = df.dropna(subset=required_cols)

    # Remove duplicates (by Management Unit Name, case insensitive)
    df["mu_name_lower"] = df["Management Unit Name"].str.lower()
    df = df.drop_duplicates(subset=["mu_name_lower"])

    with Session(database.engine) as session:
        # Existing MUs by lower name
        existing_munits = {
            name.lower()
            for (name,) in session.exec(select(ManagementUnit.name)).all()
            if name
        }

        print(existing_munits)

        # Lookup dicts for Vineyard, Variety, Status keyed by lowercase name
        vineyard_map = {v.name.lower(): v for v in session.exec(select(Vineyard)).all()}
        variety_map = {v.name.lower(): v for v in session.exec(select(Variety)).all()}
        status_map = {s.status.lower(): s for s in session.exec(select(Status)).all()}

        new_munits = []

        for _, row in df.iterrows():
            munit_name = row["Management Unit Name"]
            print(f"MANAGEMENT UNIT NAME: {munit_name}")
            munit_name_lower = munit_name.lower()
            if munit_name_lower in existing_munits:
                continue

            vineyard = vineyard_map.get(row["Vineyard Name"].lower())
            print(vineyard)
            if not vineyard:
                print(
                    f"⚠️ Vineyard '{row['Vineyard Name']}' not found, skipping MU '{munit_name}'"
                )
                continue

            variety = variety_map.get(row["Variety Name"].lower())
            print(variety)
            if not variety:
                print(f"⚠️ Variety None for MU '{munit_name}'")
                variety = None
                continue

            status = status_map.get(row["Status"].lower())
            print(status)
            if not status:
                print(
                    f"⚠️ Status '{row['Status']}' not found, skipping MU '{munit_name}'"
                )
                status = "Active"
                continue

            # Parse decimals safely
            try:
                area = Decimal(row["Management Unit Area"])
                row_width = Decimal(row["Management Unit Row Width"])
                vine_spacing = Decimal(row["Management Unit Vine Spacing"])
            except Exception as e:
                print(f"⚠️ Error parsing decimals for MU '{munit_name}': {e}")
                continue

            date_planted = parse_plant_date(row["Plant Date"])
            """ # Parse plant date
            date_planted = parse_plant_date(row["Plant Date"])
            if not date_planted:
                print(f"⚠️ Error parsing plant date for MU '{munit_name}': skipping")
                continue """

            # Parse rows total and rows start/end
            def safe_int(val):
                try:
                    return int(val) if pd.notna(val) else None
                except Exception:
                    return None

            rows_total = safe_int(row.get("Management Unit Rows Total"))

            rows_start, rows_end = parse_rows_numbers(row.get("Rows Numbers", ""))

            print(munit_name)
            print(row.get("Management Unit Variety Name Modifier" or None))
            print(area)
            print(row_width)
            print(f"vine_spacing: {vine_spacing}")
            print(f"rows_total: {rows_total}")
            print(f"rows_start_number: {rows_start}")
            print(f"rows_end_number: {rows_end}")
            print(f"date_planted: {date_planted}")
            print(f"vineyard_id: {vineyard.id}")
            print(f"variety_id: {variety.id}")
            print(f"status_id: {status.id}")

            new_munits.append(
                ManagementUnit(
                    name=munit_name,
                    variety_name_modifier=row.get(
                        "Management Unit Variety Name Modifier"
                    )
                    or None,
                    area=area,
                    row_width=row_width,
                    vine_spacing=vine_spacing,
                    rows_total=rows_total,
                    rows_start_number=rows_start,
                    rows_end_number=rows_end,
                    date_planted=date_planted,
                    vineyard_id=vineyard.id,
                    variety_id=variety.id,
                    status_id=status.id,
                )
            )
            existing_munits.add(munit_name_lower)

        if new_munits:
            session.add_all(new_munits)
            session.commit()
            print(f"✅ Imported {len(new_munits)} Management Units.")
        else:
            print("ℹ️ No new Management Units to import.")


if __name__ == "__main__":
    import_management_units("data_import_scripts/mu_import_amarok.csv")
    # import_management_units("data_import_scripts/management_units.csv")
