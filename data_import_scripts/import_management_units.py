from datetime import datetime
from decimal import Decimal

import pandas as pd
import sqlalchemy.orm as sa_orm
from sqlmodel import Session, select

import database
from data.vineyard import ManagementUnit, Status, Variety, Vineyard


def parse_rows_numbers(rows_numbers: str):
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
    if not isinstance(plant_date_str, str):
        return None
    try:
        year_part = plant_date_str.split("/")[0].strip()
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

    # Normalize and trim strings
    for col in ["Vineyard Name", "Variety Name", "Status", "Management Unit Name"]:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str).str.strip()

    # Drop rows missing required fields
    required_cols = ["Management Unit Name", "Vineyard Name"]
    df = df.dropna(subset=required_cols)

    # Deduplicate using Vineyard + MU name as composite key
    df["mu_key"] = (
        df["Vineyard Name"].str.lower().str.strip()
        + "::"
        + df["Management Unit Name"].str.lower().str.strip()
    )

    # Detect duplicates before dropping them
    duplicate_keys = df[df.duplicated(subset=["mu_key"], keep=False)]

    if not duplicate_keys.empty:
        print("⚠️ Duplicate Management Units found in CSV:")
        for _, row in duplicate_keys.iterrows():
            print(
                f"  - Vineyard: '{row['Vineyard Name']}', MU: '{row['Management Unit Name']}'"
            )

    # Now drop the actual duplicates
    df = df.drop_duplicates(subset=["mu_key"])

    with Session(database.engine) as session:
        # Load existing MUs with vineyard join
        existing_munits = {
            f"{mu.vineyard.name.lower().strip()}::{mu.name.lower().strip()}"
            for mu in session.exec(
                select(ManagementUnit).options(
                    sa_orm.joinedload(ManagementUnit.vineyard)
                )
            ).all()
        }

        vineyard_map = {v.name.lower(): v for v in session.exec(select(Vineyard)).all()}
        variety_map = {v.name.lower(): v for v in session.exec(select(Variety)).all()}
        status_map = {s.status.lower(): s for s in session.exec(select(Status)).all()}

        new_munits = []

        for _, row in df.iterrows():
            munit_name = row["Management Unit Name"].strip()
            vineyard_name = row["Vineyard Name"].strip()
            munit_key = f"{vineyard_name.lower()}::{munit_name.lower()}"

            if munit_key in existing_munits:
                continue

            vineyard = vineyard_map.get(vineyard_name.lower())
            if not vineyard:
                print(
                    f"⚠️ Vineyard '{vineyard_name}' not found, skipping MU '{munit_name}'"
                )
                continue

            variety = variety_map.get(row["Variety Name"].lower())
            if not variety:
                # print(
                #    f"⚠️ Variety '{row['Variety Name']}' not found, skipping MU '{munit_name}'"
                # )
                print("Variety is None but still adding")
                variety_id = None
            else:
                variety_id = variety.id

            status = status_map.get(row["Status"].lower())
            if not status:
                print(
                    f"⚠️ Status '{row['Status']}' not found, skipping MU '{munit_name}'"
                )
                continue

            # Safe decimal parsing
            try:
                area = Decimal(row["Management Unit Area"])
                row_width = Decimal(row["Management Unit Row Width"])
                vine_spacing = Decimal(row["Management Unit Vine Spacing"])
            except Exception as e:
                print(f"⚠️ Error parsing decimals for MU '{munit_name}': {e}")
                continue

            date_planted = parse_plant_date(row["Plant Date"])

            def safe_int(val):
                try:
                    return int(val) if pd.notna(val) else None
                except Exception:
                    return None

            rows_total = safe_int(row.get("Management Unit Rows Total"))
            rows_start, rows_end = parse_rows_numbers(row.get("Rows Numbers", ""))

            raw_modifier = row.get("Management Unit Variety Name Modifier")
            variety_name_modifier = (
                str(raw_modifier).strip() if pd.notna(raw_modifier) else None
            )

            new_munits.append(
                ManagementUnit(
                    name=munit_name,
                    variety_name_modifier=variety_name_modifier,
                    area=area,
                    row_width=row_width,
                    vine_spacing=vine_spacing,
                    rows_total=rows_total,
                    rows_start_number=rows_start,
                    rows_end_number=rows_end,
                    date_planted=date_planted,
                    vineyard_id=vineyard.id,
                    variety_id=variety_id,
                    status_id=status.id,
                )
            )
            existing_munits.add(munit_key)

        if new_munits:
            session.add_all(new_munits)
            session.commit()
            print(f"✅ Imported {len(new_munits)} Management Units.")
        else:
            print("ℹ️ No new Management Units to import.")


if __name__ == "__main__":
    import_management_units("data_import_scripts/mu_import.csv")
