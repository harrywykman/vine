from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class Vineyard(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    address: str

    management_units: list["ManagementUnit"] = Relationship(back_populates="vineyard")


class ManagementUnit(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    vineyard_id: int | None = Field(default=None, foreign_key="vineyard.id")
    vineyard: Vineyard | None = Relationship(back_populates="management_units")
