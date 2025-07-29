import datetime
from decimal import Decimal
from typing import List, Optional

import sqlalchemy as sa
from geoalchemy2 import Geometry
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import Polygon
from sqlmodel import Field, Relationship, SQLModel

###### CORE VINEYARD MODELS ########


class Vineyard(SQLModel, table=True):
    __tablename__ = "vineyards"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True, nullable=False)
    address: Optional[str] = Field(default=None)

    # PostGIS polygon field for vineyard boundary
    boundary: Optional[str] = Field(
        default=None,
        sa_column=sa.Column(Geometry("POLYGON", srid=4326)),
        description="Vineyard boundary as a polygon in WGS84 (EPSG:4326)",
    )

    management_units: List["ManagementUnit"] = Relationship(back_populates="vineyard")

    def __str__(self):
        return f"{self.name}"

    @property
    def boundary_geojson(self):
        """Convert PostGIS geometry to GeoJSON for frontend use"""
        if self.boundary:
            shape = to_shape(self.boundary)
            return {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [list(shape.exterior.coords)],
                },
                "properties": {"name": self.name, "type": "vineyard"},
            }
        return None

    def set_boundary_from_coordinates(self, coordinates: List[List[float]]):
        """Set boundary from list of [lng, lat] coordinates"""
        if coordinates and len(coordinates) >= 3:
            # Ensure the polygon is closed
            if coordinates[0] != coordinates[-1]:
                coordinates.append(coordinates[0])

            polygon = Polygon(coordinates)
            self.boundary = from_shape(polygon, srid=4326)


class ManagementUnit(SQLModel, table=True):
    __tablename__ = "management_units"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    variety_name_modifier: Optional[str] = Field(default=None)

    area: Decimal = Field(sa_column=sa.Column(sa.Numeric(5, 2)))
    row_width: Decimal = Field(sa_column=sa.Column(sa.Numeric(2, 1)))
    vine_spacing: Decimal = Field(sa_column=sa.Column(sa.Numeric(2, 1)))

    rows_total: Optional[int] = Field(default=None)
    rows_start_number: Optional[int] = Field(default=None)
    rows_end_number: Optional[int] = Field(default=None)
    date_planted: datetime.datetime | None = Field(sa_column=sa.Column(sa.Date))

    # PostGIS polygon field for management unit area
    area_polygon: Optional[str] = Field(
        default=None,
        sa_column=sa.Column(Geometry("POLYGON", srid=4326)),
        description="Management unit area as a polygon in WGS84 (EPSG:4326)",
    )

    spray_records: List["SprayRecord"] = Relationship(back_populates="management_unit")

    variety_id: int | None = Field(default=None, foreign_key="varieties.id")
    vineyard_id: int | None = Field(
        default=None, foreign_key="vineyards.id", ondelete="CASCADE"
    )
    status_id: int | None = Field(default=None, foreign_key="states.id")

    variety: "Variety" | None = Relationship(back_populates="management_units")
    vineyard: "Vineyard" | None = Relationship(back_populates="management_units")
    status: "Status" | None = Relationship(back_populates="management_units")

    def __str__(self):
        return f"{self.name}"

    @property
    def name_with_variety(self):
        if self.variety:
            return f"{self.name} - {self.variety.name}"
        return None

    @property
    def area_polygon_geojson(self):
        """Convert PostGIS geometry to GeoJSON for frontend use"""
        if self.area_polygon:
            shape = to_shape(self.area_polygon)
            return {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [list(shape.exterior.coords)],
                },
                "properties": {
                    "name": self.name,
                    "variety": self.variety.name if self.variety else None,
                    "area": float(self.area),
                    "type": "management_unit",
                },
            }
        return None

    def set_area_polygon_from_coordinates(self, coordinates: List[List[float]]):
        """Set area polygon from list of [lng, lat] coordinates"""
        if coordinates and len(coordinates) >= 3:
            # Ensure the polygon is closed
            if coordinates[0] != coordinates[-1]:
                coordinates.append(coordinates[0])

            polygon = Polygon(coordinates)
            self.area_polygon = from_shape(polygon, srid=4326)

    @property
    def calculated_area_hectares(self):
        """Calculate area in hectares from the polygon geometry"""
        if self.area_polygon:
            # Convert to a projected coordinate system for accurate area calculation
            # This is a simplified example - you'd want to use an appropriate local projection
            shape = to_shape(self.area_polygon)
            # For rough calculation in WGS84 (not accurate for precise measurements)
            return shape.area * 111319.9 * 111319.9 / 10000  # Convert to hectares
        return None


class Variety(SQLModel, table=True):
    __tablename__ = "varieties"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)  # e.g. "Cabernet Sauvignon"
    wine_colour_id: int = Field(foreign_key="wine_colours.id")

    wine_colour: "WineColour" = Relationship(back_populates="varieties")
    management_units: List["ManagementUnit"] = Relationship(back_populates="variety")

    def __str__(self):
        return f"{self.name}"


class Status(SQLModel, table=True):
    __tablename__ = "states"

    id: Optional[int] = Field(default=None, primary_key=True)
    status: str = Field(default="Active")

    management_units: List["ManagementUnit"] = Relationship(back_populates="status")

    def __str__(self):
        return f"{self.status}"


class WineColour(SQLModel, table=True):
    __tablename__ = "wine_colours"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)  # e.g. "Red", "White"

    varieties: List["Variety"] = Relationship(back_populates="wine_colour")

    def __str__(self):
        return f"{self.name}"

    def is_red(self):
        return self.name == "Red"

    def is_white(self):
        return self.name == "White"


# ... (rest of your existing models remain unchanged)


###### HELPER FUNCTIONS FOR GEOSPATIAL OPERATIONS ########


def create_vineyard_with_boundary(
    name: str, address: str, coordinates: List[List[float]]
):
    """Helper function to create a vineyard with a boundary polygon"""
    vineyard = Vineyard(name=name, address=address)
    vineyard.set_boundary_from_coordinates(coordinates)
    return vineyard


def create_management_unit_with_area(
    name: str,
    area: Decimal,
    coordinates: List[List[float]],
    vineyard_id: int,
    variety_id: int = None,
):
    """Helper function to create a management unit with an area polygon"""
    management_unit = ManagementUnit(
        name=name, area=area, vineyard_id=vineyard_id, variety_id=variety_id
    )
    management_unit.set_area_polygon_from_coordinates(coordinates)
    return management_unit


def get_management_units_within_boundary(session, boundary_wkt: str):
    """Query management units within a given boundary using PostGIS"""
    from sqlalchemy import text

    query = text("""
        SELECT mu.* 
        FROM management_units mu 
        WHERE ST_Within(mu.area_polygon, ST_GeomFromText(:boundary, 4326))
    """)

    result = session.execute(query, {"boundary": boundary_wkt})
    return result.fetchall()


def get_nearby_management_units(
    session, point_lat: float, point_lng: float, distance_km: float = 1.0
):
    """Find management units within a certain distance of a point"""
    from sqlalchemy import text

    query = text("""
        SELECT mu.*, ST_Distance(
            ST_Transform(mu.area_polygon, 3857), 
            ST_Transform(ST_SetSRID(ST_MakePoint(:lng, :lat), 4326), 3857)
        ) / 1000 as distance_km
        FROM management_units mu 
        WHERE ST_DWithin(
            ST_Transform(mu.area_polygon, 3857), 
            ST_Transform(ST_SetSRID(ST_MakePoint(:lng, :lat), 4326), 3857), 
            :distance_m
        )
        ORDER BY distance_km
    """)

    result = session.execute(
        query, {"lat": point_lat, "lng": point_lng, "distance_m": distance_km * 1000}
    )
    return result.fetchall()
