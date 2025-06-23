from datetime import datetime
from decimal import Decimal

import pandas as pd

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

REQUIRED_NUMERIC_FIELDS = [
    "Management Unit Area",
    "Management Unit Row Width",
    "Management Unit Vine Spacing",
]


def safe_decimal(val):
    try:
        return Decimal(str(val))
    except:
        return None


def safe_date(val):
    if pd.isna(val) or not str(val).strip():
        return None
    try:
        year_str = str(val).split("/")[0].strip()
        return datetime.strptime(year_str, "%Y").date()
    except:
        return None


def validate_csv(csv_path):
    df = pd.read_csv(csv_path, names=CSV_COLUMNS, header=0, dtype=str)

    print(f"🔍 Checking {len(df)} rows...\n")
    issues = 0

    for idx, row in df.iterrows():
        row_num = idx + 2  # since header is row 1

        # Column count validation (in case CSV is malformed)
        if len(row) != len(CSV_COLUMNS):
            print(
                f"❌ Row {row_num}: Incorrect column count ({len(row)} vs {len(CSV_COLUMNS)})"
            )
            issues += 1
            continue

        # Required numeric field checks
        for field in REQUIRED_NUMERIC_FIELDS:
            val = row.get(field)
            if safe_decimal(val) is None:
                print(f"❌ Row {row_num}: Invalid number in '{field}' → {val}")
                issues += 1

        # Date parsing
        date_val = row.get("Plant Date", "")
        if safe_date(date_val) is None and str(date_val).strip():
            print(f"❌ Row {row_num}: Invalid Plant Date format → {date_val}")
            issues += 1

    if issues == 0:
        print("✅ CSV validation passed. No issues found.")
    else:
        print(f"\n⚠️ {issues} issue(s) found. Please review above.")


if __name__ == "__main__":
    validate_csv("management_units.csv")
