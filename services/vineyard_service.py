from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from data.vineyard import ManagementUnit, Vineyard


def all_vineyards(session: Session):
    query = select(Vineyard)

    vineyards = session.exec(query)
    return vineyards


def get_vineyard_by_id(session: Session, id: int):
    print("GETTING VINEYARD BY ID")
    vineyard = session.get(Vineyard, id)
    if not vineyard:
        raise HTTPException(status_code=404, detail="Vineyard not found")
    return vineyard


def eagerly_get_vineyard_managment_units_by_id(session: Session, id: int):
    management_units = session.exec(
        select(ManagementUnit)
        .where(ManagementUnit.vineyard_id == id)
        .order_by(ManagementUnit.name)
        .options(
            selectinload(ManagementUnit.variety),
            selectinload(ManagementUnit.status),
        )
    ).all()
    return management_units
