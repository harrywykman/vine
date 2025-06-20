from fastapi import Depends
from dependencies import get_session
from data.vineyard import Vineyard
import database

from sqlmodel import Session, select

def all_vineyards():
    session = next(get_session())

    query = select(Vineyard)

    vineyards = session.exec(query)
    return vineyards


def get_vineyard_by_id(id: int):

    print("GETTING VINEYARD BY ID")
    with Session(database.engine) as session:
        vineyard = session.get(Vineyard, id)
    if not vineyard:
        raise HTTPException(status_code=404, detail="Vineyard not found")
    return vineyard


def get_vineyard_managment_units_by_id(id: int):
    with Session(database.engine) as session:
        vineyard = session.get(Vineyard, id)
        management_units = vineyard.management_units
    return management_units
