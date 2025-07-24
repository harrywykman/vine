"""
Polygon Batch Importer - Dictionary Workflow
Efficiently import vineyard boundaries and management unit polygons
"""

from typing import Any, Dict, List, Optional

from sqlmodel import Session

from services import vineyard_service

# =============================================================================
# DATA STRUCTURE - Add your polygon data here
# =============================================================================

VINEYARD_POLYGONS = {
    "Kaards": {
        "boundary": [
            [-33.731649, 115.022475],
            [-33.737303, 115.022367],
            [-33.737314, 115.016831],
            [-33.735683, 115.0146],
            [-33.735522, 115.014578],
            [-33.734589, 115.01504],
            [-33.732851, 115.015394],
            [-33.731756, 115.015447],
            [-33.73166, 115.015501],
            [-33.731649, 115.022475],
        ],
        "management_units": {
            "3a": [
                [-33.73435, 115.01688],
                [-33.7342, 115.01673],
                [-33.73477, 115.01514],
                [-33.73505, 115.01503],
            ],
            "1": [
                [-33.7346, 115.01746],
                [-33.73549, 115.01504],
                [-33.73668, 115.0162],
                [-33.73684, 115.01654],
                [-33.73677, 115.01691],
                [-33.73643, 115.01783],
                [-33.73627, 115.01817],
                [-33.73608, 115.01812],
                [-33.73507, 115.01817],
                [-33.73462, 115.01784],
                [-33.7346, 115.01746],
            ],
            "2": [
                [-33.73546, 115.01503],
                [-33.7346, 115.01741],
                [-33.73439, 115.01688],
                [-33.73504, 115.01505],
                [-33.7353, 115.01489],
            ],
            "3b": [
                [-33.73418, 115.0167],
                [-33.73471, 115.01518],
                [-33.73443, 115.0153],
                [-33.73401, 115.01651],
            ],
        },
    },
    "Vintage Unit": {
        "boundary": [
            [-33.76004, 115.04992],
            [-33.76249, 115.0488],
            [-33.76485, 115.04696],
            [-33.76486, 115.05558],
            [-33.76351, 115.05628],
        ],
        "management_units": {
            "3": [
                [-33.76196, 115.04922],
                [-33.76041, 115.04991],
                [-33.76039, 115.05017],
                [-33.76088, 115.05105],
                [-33.76124, 115.05135],
                [-33.76163, 115.05205],
                [-33.76213, 115.05183],
                [-33.76179, 115.05089],
            ],
            "1": [
                [-33.76292, 115.04868],
                [-33.76436, 115.05022],
                [-33.76451, 115.04992],
                [-33.76483, 115.04954],
                [-33.76482, 115.04795],
                [-33.76439, 115.04752],
            ],
            "2": [
                [-33.76434, 115.05025],
                [-33.7629, 115.0487],
                [-33.76254, 115.04897],
                [-33.7624, 115.04948],
                [-33.76239, 115.05066],
                [-33.76305, 115.05138],
                [-33.7633, 115.05157],
                [-33.76364, 115.05183],
            ],
        },
    },
    "Amarok": {
        "boundary": [
            [-33.74544, 115.021],
            [-33.74137, 115.021],
            [-33.74136, 115.02194],
            [-33.7404, 115.02196],
            [-33.73866, 115.01974],
            [-33.73737, 115.01977],
            [-33.73738, 115.01684],
            [-33.74543, 115.01679],
            [-33.74544, 115.021],
        ],
        "management_units": {
            "8": [
                [-33.74355, 115.02022],
                [-33.74397, 115.02025],
                [-33.744, 115.01718],
                [-33.74379, 115.01717],
                [-33.74371, 115.01787],
                [-33.74355, 115.01801],
            ],
            "9": [
                [-33.74398, 115.02027],
                [-33.74409, 115.02038],
                [-33.7441, 115.02092],
                [-33.74526, 115.02093],
                [-33.74536, 115.02077],
                [-33.74536, 115.01715],
                [-33.74523, 115.01699],
                [-33.74472, 115.01699],
                [-33.74437, 115.01715],
                [-33.74401, 115.01715],
            ],
            "3": [
                [-33.73877, 115.01903],
                [-33.74041, 115.01902],
                [-33.74041, 115.01975],
                [-33.73916, 115.01975],
                [-33.73906, 115.0196],
                [-33.73877, 115.0196],
            ],
            "2": [
                [-33.73794, 115.01694],
                [-33.73793, 115.0196],
                [-33.73869, 115.0196],
                [-33.73869, 115.01694],
            ],
            "4": [
                [-33.74102, 115.01697],
                [-33.741, 115.02176],
                [-33.74133, 115.02177],
                [-33.74133, 115.01858],
                [-33.74157, 115.01822],
                [-33.74158, 115.01698],
            ],
            "5": [
                [-33.74101, 115.01697],
                [-33.74098, 115.02177],
                [-33.74051, 115.02177],
                [-33.74051, 115.01698],
            ],
            "1": [
                [-33.73739, 115.01695],
                [-33.73793, 115.01694],
                [-33.73792, 115.0196],
                [-33.73739, 115.0196],
            ],
            "7": [
                [-33.74353, 115.02023],
                [-33.74353, 115.018],
                [-33.74267, 115.01837],
                [-33.74266, 115.02091],
                [-33.74328, 115.02091],
                [-33.74328, 115.02043],
            ],
            "6": [
                [-33.74135, 115.02091],
                [-33.74265, 115.02091],
                [-33.74265, 115.01838],
                [-33.74239, 115.01859],
                [-33.74219, 115.01878],
                [-33.74194, 115.01893],
                [-33.74172, 115.01899],
                [-33.74136, 115.01899],
            ],
        },
    },
}

# =============================================================================
# BATCH IMPORT FUNCTIONS
# =============================================================================


def validate_coordinates(coords: List[List[float]], name: str) -> bool:
    """Validate coordinate data"""
    if not coords:
        print(f"Warning: No coordinates provided for {name}")
        return False

    if len(coords) < 3:
        print(f"Error: {name} needs at least 3 coordinates for a polygon")
        return False

    # Check coordinate format
    for i, coord in enumerate(coords):
        if len(coord) != 2:
            print(f"Error: {name} coordinate {i} is not [lat, lng] format")
            return False

        lat, lng = coord
        if not (-90 <= lat <= 90):
            print(f"Error: {name} coordinate {i} has invalid latitude: {lat}")
            return False

        if not (-180 <= lng <= 180):
            print(f"Error: {name} coordinate {i} has invalid longitude: {lng}")
            return False

    return True


def convert_to_postgis_coords(coords: List[List[float]]) -> List[List[float]]:
    """Convert [lat, lng] to [lng, lat] for PostGIS"""
    return [[coord[1], coord[0]] for coord in coords]


def import_vineyard_boundary(
    session: Session, vineyard_name: str, boundary_coords: List[List[float]]
) -> bool:
    """Import vineyard boundary polygon"""
    try:
        # Validate coordinates
        if not validate_coordinates(boundary_coords, f"{vineyard_name} boundary"):
            return False

        # Get vineyard
        vineyard = vineyard_service.get_vineyard_by_name(session, vineyard_name)
        if not vineyard:
            print(f"Error: Vineyard '{vineyard_name}' not found in database")
            return False

        # Convert and set boundary
        postgis_coords = convert_to_postgis_coords(boundary_coords)
        vineyard.set_boundary_from_coordinates(postgis_coords)
        session.add(vineyard)

        print(
            f"✓ Set boundary for vineyard '{vineyard_name}' ({len(boundary_coords)} points)"
        )
        return True

    except Exception as e:
        print(f"Error setting boundary for {vineyard_name}: {e}")
        return False


def import_management_unit_polygon(
    session: Session, vineyard_name: str, unit_name: str, unit_coords: List[List[float]]
) -> bool:
    """Import management unit polygon"""
    try:
        # Validate coordinates
        if not validate_coordinates(unit_coords, f"{vineyard_name} - {unit_name}"):
            return False

        # Get vineyard
        vineyard = vineyard_service.get_vineyard_by_name(session, vineyard_name)
        if not vineyard:
            print(f"Error: Vineyard '{vineyard_name}' not found")
            return False

        # Find management unit
        unit = None
        for mu in vineyard.management_units:
            if mu.name == unit_name:
                unit = mu
                break

        if not unit:
            print(
                f"Error: Management unit '{unit_name}' not found in vineyard '{vineyard_name}'"
            )
            return False

        # Convert and set polygon
        postgis_coords = convert_to_postgis_coords(unit_coords)
        unit.set_area_polygon_from_coordinates(postgis_coords)
        session.add(unit)

        print(
            f"✓ Set polygon for '{unit_name}' in '{vineyard_name}' ({len(unit_coords)} points)"
        )
        return True

    except Exception as e:
        print(f"Error setting polygon for {unit_name}: {e}")
        return False


def batch_import_polygons(
    session: Session, data: Dict[str, Any], dry_run: bool = False
) -> Dict[str, Any]:
    """
    Main batch import function

    Args:
        session: Database session
        data: Dictionary of vineyard polygon data
        dry_run: If True, validate but don't commit changes

    Returns:
        Dictionary with import results
    """
    results = {
        "vineyards_processed": 0,
        "boundaries_imported": 0,
        "management_units_imported": 0,
        "errors": [],
    }

    print("=" * 60)
    print(f"POLYGON BATCH IMPORT {'(DRY RUN)' if dry_run else ''}")
    print("=" * 60)

    try:
        for vineyard_name, vineyard_data in data.items():
            print(f"\nProcessing vineyard: {vineyard_name}")
            results["vineyards_processed"] += 1

            # Import vineyard boundary
            if "boundary" in vineyard_data and vineyard_data["boundary"]:
                if import_vineyard_boundary(
                    session, vineyard_name, vineyard_data["boundary"]
                ):
                    results["boundaries_imported"] += 1

            # Import management unit polygons
            if "management_units" in vineyard_data:
                for unit_name, unit_coords in vineyard_data["management_units"].items():
                    if import_management_unit_polygon(
                        session, vineyard_name, unit_name, unit_coords
                    ):
                        results["management_units_imported"] += 1

        # Commit changes (unless dry run)
        if not dry_run:
            session.commit()
            print("\n✓ All changes committed to database")
        else:
            session.rollback()
            print("\n• Dry run complete - no changes made")

    except Exception as e:
        session.rollback()
        error_msg = f"Batch import failed: {e}"
        results["errors"].append(error_msg)
        print(f"\n✗ {error_msg}")

    # Print summary
    print("\n" + "=" * 60)
    print("IMPORT SUMMARY")
    print("=" * 60)
    print(f"Vineyards processed: {results['vineyards_processed']}")
    print(f"Boundaries imported: {results['boundaries_imported']}")
    print(f"Management units imported: {results['management_units_imported']}")

    if results["errors"]:
        print(f"Errors: {len(results['errors'])}")
        for error in results["errors"]:
            print(f"  - {error}")

    return results


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def quick_add_single_polygon(
    session: Session,
    vineyard_name: str,
    coordinates: List[List[float]],
    unit_name: Optional[str] = None,
):
    """
    Quick function to add a single polygon

    Args:
        session: Database session
        vineyard_name: Name of vineyard
        coordinates: List of [lat, lng] coordinates
        unit_name: Management unit name (None for vineyard boundary)
    """
    if unit_name:
        success = import_management_unit_polygon(
            session, vineyard_name, unit_name, coordinates
        )
    else:
        success = import_vineyard_boundary(session, vineyard_name, coordinates)

    if success:
        session.commit()
        print("✓ Polygon added successfully")
    else:
        session.rollback()
        print("✗ Failed to add polygon")


def list_vineyard_data(session: Session):
    """List all vineyards and their management units for reference"""
    print("\n" + "=" * 60)
    print("VINEYARD DATA REFERENCE")
    print("=" * 60)

    vineyards = vineyard_service.get_all_vineyards(session)

    for vineyard in vineyards:
        print(f"\nVineyard: {vineyard.name}")
        print(f"  Has boundary: {'Yes' if vineyard.boundary else 'No'}")

        if vineyard.management_units:
            print("  Management units:")
            for unit in vineyard.management_units:
                has_polygon = "Yes" if unit.area_polygon else "No"
                print(f"    - {unit.name} (polygon: {has_polygon})")
        else:
            print("  Management units: None")


# =============================================================================
# MAIN EXECUTION
# =============================================================================


def main():
    """Main execution function"""
    from database import engine

    with Session(engine) as session:
        print("Starting polygon batch import...")

        # Optional: List existing data first
        # list_vineyard_data(session)

        # Run dry run first to validate
        print("\n1. Running validation (dry run)...")
        results = batch_import_polygons(session, VINEYARD_POLYGONS, dry_run=True)

        if results["errors"]:
            print("\n✗ Validation failed. Please fix errors before importing.")
            return

        # Confirm before actual import
        response = input("\n2. Validation passed. Proceed with import? (y/N): ")
        if response.lower() != "y":
            print("Import cancelled.")
            return

        # Run actual import
        print("\n3. Running actual import...")
        final_results = batch_import_polygons(session, VINEYARD_POLYGONS, dry_run=False)

        if not final_results["errors"]:
            print("\n🎉 Import completed successfully!")
        else:
            print("\n⚠️  Import completed with errors. Check output above.")


# =============================================================================
# USAGE EXAMPLES
# =============================================================================

if __name__ == "__main__":
    # Method 1: Run the full batch import
    main()

    # Method 2: Quick single polygon add
    # from database import engine
    # with Session(engine) as session:
    #     coords = [
    #         [-33.74544, 115.021],
    #         [-33.74137, 115.021],
    #         [-33.74136, 115.02194],
    #         [-33.74543, 115.01679],
    #     ]
    #     quick_add_single_polygon(session, "Amarok", coords)  # For vineyard boundary
    #     quick_add_single_polygon(session, "Amarok", coords, "Block A")  # For management unit
