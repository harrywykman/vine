"""
Polygon Template Generator
Creates a dictionary template from existing database data for use with the polygon batch importer
"""

from typing import Any, Dict, List, Optional

from sqlmodel import Session

from services import vineyard_service

# =============================================================================
# TEMPLATE GENERATION FUNCTIONS
# =============================================================================


def generate_polygon_template(
    session: Session,
    include_existing_polygons: bool = True,
    vineyard_filter: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Generate a polygon template dictionary from database data

    Args:
        session: Database session
        include_existing_polygons: If True, includes existing polygon coordinates
        vineyard_filter: Optional list of vineyard names to include (None for all)

    Returns:
        Dictionary template ready for polygon import
    """
    template = {}

    # Get all vineyards or filtered list
    all_vineyards = vineyard_service.all_vineyards(session)

    if vineyard_filter:
        vineyards = [v for v in all_vineyards if v.name in vineyard_filter]
    else:
        vineyards = all_vineyards

    for vineyard in vineyards:
        vineyard_data = {}

        # Add boundary (existing or placeholder)
        if include_existing_polygons and vineyard.boundary:
            # Get existing boundary coordinates
            vineyard_data["boundary"] = vineyard.boundary_coordinates
        else:
            # Add placeholder
            vineyard_data["boundary"] = [
                # [lat, lng],
                # [lat, lng],
                # Add your boundary coordinates here
            ]

        # Add management units
        if vineyard.management_units:
            vineyard_data["management_units"] = {}

            for unit in vineyard.management_units:
                if include_existing_polygons and unit.area_polygon:
                    # Get existing polygon coordinates
                    vineyard_data["management_units"][unit.name] = (
                        unit.area_coordinates_lat_long()
                    )
                else:
                    # Add placeholder
                    vineyard_data["management_units"][unit.name] = [
                        # [lat, lng],
                        # [lat, lng],
                        # Add coordinates for unit.name here
                    ]
        else:
            vineyard_data["management_units"] = {
                # "Unit Name": [
                #     [lat, lng],
                #     [lat, lng],
                # ]
            }

        template[vineyard.name] = vineyard_data

    return template


def format_template_as_python_code(
    template: Dict[str, Any], variable_name: str = "VINEYARD_POLYGONS"
) -> str:
    """
    Format template dictionary as Python code string

    Args:
        template: Template dictionary
        variable_name: Python variable name for the dictionary

    Returns:
        Formatted Python code string
    """

    def format_coordinates(coords):
        """Format coordinate list for Python code"""
        if not coords:
            return "[\n        # [lat, lng],\n        # [lat, lng],\n        # Add your coordinates here\n    ]"

        # Format existing coordinates
        formatted = "[\n"
        for coord in coords:
            formatted += f"        {coord},\n"
        formatted += "    ]"
        return formatted

    def format_management_units(units):
        """Format management units dictionary"""
        if not units:
            return '{\n        # "Unit Name": [\n        #     [lat, lng],\n        #     [lat, lng],\n        # ]\n    }'

        formatted = "{\n"
        for unit_name, coords in units.items():
            formatted += f'        "{unit_name}": {format_coordinates(coords)},\n'
        formatted += "    }"
        return formatted

    # Start building the code string
    code = f"{variable_name} = {{\n"

    for vineyard_name, vineyard_data in template.items():
        code += f'    "{vineyard_name}": {{\n'

        # Add boundary
        boundary_coords = vineyard_data.get("boundary", [])
        code += f'        "boundary": {format_coordinates(boundary_coords)},\n'

        # Add management units
        units = vineyard_data.get("management_units", {})
        code += f'        "management_units": {format_management_units(units)}\n'

        code += "    },\n\n"

    code += "}"

    return code


def save_template_to_file(template_code: str, filename: str = "polygon_template.py"):
    """Save template to Python file"""
    header = '''"""
Generated Polygon Template
Auto-generated from database data for use with polygon batch importer

Usage:
1. Fill in the coordinate arrays with your polygon data
2. Import this file in your polygon batch importer
3. Run the batch import

Coordinate format: [lat, lng]
"""

'''

    with open(filename, "w") as f:
        f.write(header)
        f.write(template_code)

    print(f"✓ Template saved to {filename}")


def print_summary(template: Dict[str, Any]):
    """Print a summary of the generated template"""
    print("\n" + "=" * 60)
    print("TEMPLATE SUMMARY")
    print("=" * 60)

    total_vineyards = len(template)
    total_units = sum(len(v.get("management_units", {})) for v in template.values())

    vineyards_with_boundaries = sum(
        1
        for v in template.values()
        if v.get("boundary") and len(v["boundary"]) > 0 and v["boundary"][0] != []
    )

    units_with_polygons = sum(
        1
        for v in template.values()
        for unit_coords in v.get("management_units", {}).values()
        if unit_coords and len(unit_coords) > 0 and unit_coords[0] != []
    )

    print(f"Total vineyards: {total_vineyards}")
    print(f"Total management units: {total_units}")
    print(f"Vineyards with existing boundaries: {vineyards_with_boundaries}")
    print(f"Management units with existing polygons: {units_with_polygons}")
    print(
        f"Vineyards needing boundaries: {total_vineyards - vineyards_with_boundaries}"
    )
    print(f"Management units needing polygons: {total_units - units_with_polygons}")

    print("\nVineyard breakdown:")
    for vineyard_name, vineyard_data in template.items():
        boundary_status = (
            "✓"
            if (
                vineyard_data.get("boundary")
                and len(vineyard_data["boundary"]) > 0
                and vineyard_data["boundary"][0] != []
            )
            else "✗"
        )

        unit_count = len(vineyard_data.get("management_units", {}))
        units_with_coords = sum(
            1
            for coords in vineyard_data.get("management_units", {}).values()
            if coords and len(coords) > 0 and coords[0] != []
        )

        print(
            f"  {vineyard_name}: boundary {boundary_status}, units {units_with_coords}/{unit_count}"
        )


# =============================================================================
# ANALYSIS FUNCTIONS
# =============================================================================


def analyze_existing_polygons(session: Session):
    """Analyze existing polygon data in the database"""
    print("\n" + "=" * 60)
    print("EXISTING POLYGON ANALYSIS")
    print("=" * 60)

    vineyards = vineyard_service.all_vineyards(session)

    for vineyard in vineyards:
        print(f"\nVineyard: {vineyard.name}")

        # Check vineyard boundary
        if vineyard.boundary:
            coords = vineyard.boundary_coordinates
            if coords:
                print(f"  Boundary: ✓ ({len(coords)} points)")
                # Print first few coordinates as sample
                if len(coords) > 0:
                    print(
                        f"    Sample: {coords[0]} -> {coords[1] if len(coords) > 1 else 'N/A'}"
                    )
            else:
                print("  Boundary: ✗ (exists but no coordinates)")
        else:
            print("  Boundary: ✗ (missing)")

        # Check management units
        if vineyard.management_units:
            print(f"  Management units ({len(vineyard.management_units)}):")
            for unit in vineyard.management_units:
                if unit.area_polygon:
                    coords = unit.area_coordinates_lat_long()
                    if coords:
                        print(f"    {unit.name}: ✓ ({len(coords)} points)")
                    else:
                        print(f"    {unit.name}: ✗ (exists but no coordinates)")
                else:
                    print(f"    {unit.name}: ✗ (missing)")
        else:
            print("  Management units: None")


# =============================================================================
# MAIN EXECUTION FUNCTIONS
# =============================================================================


def generate_full_template(
    session: Session,
    filename: str = "polygon_template.py",
    include_existing: bool = True,
    vineyard_filter: Optional[List[str]] = None,
):
    """
    Generate and save a complete polygon template

    Args:
        session: Database session
        filename: Output filename
        include_existing: Include existing polygon coordinates
        vineyard_filter: Optional list of vineyard names to include
    """
    print("Generating polygon template...")

    # Generate template
    template = generate_polygon_template(session, include_existing, vineyard_filter)

    # Format as Python code
    template_code = format_template_as_python_code(template)

    # Save to file
    save_template_to_file(template_code, filename)

    # Print summary
    print_summary(template)

    print("\n✓ Template generation complete!")
    print(f"✓ Template saved to: {filename}")
    print("✓ Ready for polygon coordinate input")


def generate_empty_template(
    session: Session,
    filename: str = "polygon_template_empty.py",
    vineyard_filter: Optional[List[str]] = None,
):
    """Generate template with no existing coordinates (empty placeholders only)"""
    print("Generating empty polygon template...")
    generate_full_template(
        session, filename, include_existing=False, vineyard_filter=vineyard_filter
    )


def generate_specific_vineyards_template(
    session: Session,
    vineyard_names: List[str],
    filename: str = "polygon_template_specific.py",
    include_existing: bool = True,
):
    """Generate template for specific vineyards only"""
    print(f"Generating template for vineyards: {', '.join(vineyard_names)}")
    generate_full_template(session, filename, include_existing, vineyard_names)


# =============================================================================
# MAIN EXECUTION
# =============================================================================


def main():
    """Main execution with options"""
    from database import engine

    with Session(engine) as session:
        print("Polygon Template Generator")
        print("=" * 40)

        # Show analysis first
        analyze_existing_polygons(session)

        print("\nTemplate Generation Options:")
        print("1. Full template (includes existing coordinates)")
        print("2. Empty template (placeholders only)")
        print("3. Specific vineyards only")
        print("4. Analysis only (no template generation)")

        choice = input("\nSelect option (1-4): ").strip()

        if choice == "1":
            generate_full_template(session)
        elif choice == "2":
            generate_empty_template(session)
        elif choice == "3":
            # Get vineyard names
            vineyards = vineyard_service.all_vineyards(session)
            print("\nAvailable vineyards:")
            for i, v in enumerate(vineyards, 1):
                print(f"  {i}. {v.name}")

            selected = input("\nEnter vineyard names (comma-separated): ").strip()
            vineyard_names = [name.strip() for name in selected.split(",")]

            generate_specific_vineyards_template(session, vineyard_names)
        elif choice == "4":
            print("\nAnalysis complete. No template generated.")
        else:
            print("Invalid choice. Exiting.")


if __name__ == "__main__":
    main()

# =============================================================================
# USAGE EXAMPLES
# =============================================================================

"""
Usage Examples:

1. Generate full template:
   python polygon_template_generator.py

2. Programmatic usage:
   from database import engine
   from sqlmodel import Session
   
   with Session(engine) as session:
       # Generate template with existing coordinates
       generate_full_template(session, "my_template.py")
       
       # Generate empty template
       generate_empty_template(session, "empty_template.py")
       
       # Generate for specific vineyards
       generate_specific_vineyards_template(session, ["Amarok", "Other Vineyard"])
       
       # Just analyze existing data
       analyze_existing_polygons(session)
"""
