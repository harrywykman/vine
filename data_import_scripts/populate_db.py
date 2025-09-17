from data_import_scripts import (
    import_chemical_groups,
    import_chemicals_and_groups,
    import_EL_growth_stage,
    import_management_units,
    import_reentry_periods,
    import_states,
    import_users_from_json,
    import_varieties,
    import_vineyards,
)
from data_import_scripts.geo_data import polygon_import

# Run as module from root dir:  python -m data_import_scripts.populate_db


def populate_db():
    import_vineyards.import_vineyards("data_import_scripts/vineyards.csv")
    import_varieties.import_varieties("data_import_scripts/varieties.csv")
    import_states.insert_or_update_states()
    import_management_units.import_management_units("data_import_scripts/mu_import.csv")
    import_EL_growth_stage.seed_growth_stages()
    import_reentry_periods.seed_reentry_periods()
    import_chemical_groups.populate_chemical_groups()
    import_chemicals_and_groups.import_chemicals_from_json(
        "./data_import_scripts/chemicals_export.json"
    )
    import_users_from_json.import_new_users()
    # import_users.import_new_users()
    # import_chemicals.import_chemicals("./data_import_scripts/chemicals.csv")
    polygon_import.main()


if __name__ == "__main__":
    populate_db()
