from typing import List

from sqlmodel import Session

from services import vineyard_service

name = "Amarok"
amarok_boundary = [
    [-33.74544, 115.021],
    [-33.74137, 115.021],
    [-33.74136, 115.02194],
    [-33.7404, 115.02196],
    [-33.73866, 115.01974],
    [-33.73737, 115.01977],
    [-33.73738, 115.01684],
    [-33.74543, 115.01679],
]


def add_boundary(session: Session, name: str, coords: List[List[float]]):
    """
    Add a boundary polygon to an existing vineyard.

    Args:
        session: SQLModel database session
        name: Name of the vineyard
        coords: List of [lat, lng] coordinate pairs
    """
    # Get the vineyard by name
    vineyard = vineyard_service.get_vineyard_by_name(session=session, name=name)

    if not vineyard:
        raise ValueError(f"Vineyard with name '{name}' not found")

    # Convert [lat, lng] to [lng, lat] for PostGIS
    # PostGIS expects longitude first, then latitude
    postgis_coords = [[coord[1], coord[0]] for coord in coords]

    # Set the boundary using the corrected coordinates
    vineyard.set_boundary_from_coordinates(postgis_coords)

    # Add the vineyard to the session and commit
    session.add(vineyard)
    session.commit()
    session.refresh(vineyard)

    print(f"Boundary added successfully to vineyard '{name}'")
    return vineyard


# Usage example:
# Assuming you have a session and the vineyard exists
def main():
    from database import engine

    # SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        try:
            updated_vineyard = add_boundary(session, name, amarok_boundary)

            # Verify the boundary was set
            if updated_vineyard.boundary:
                print(f"Boundary successfully added to {updated_vineyard.name}")

                # Get GeoJSON representation for frontend use
                geojson = updated_vineyard.boundary_geojson
                if geojson:
                    print(f"GeoJSON coordinates: {geojson['geometry']['coordinates']}")
            else:
                print("Warning: Boundary was not set properly")

        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            session.rollback()
            print(f"Database error: {e}")


if __name__ == "__main__":
    main()
