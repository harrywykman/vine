from sqlmodel import Session, select

from data.vineyard import Chemical


def all_chemicals(session: Session):
    query = select(Chemical).order_by(Chemical.name)

    chemicals = session.exec(query)
    return chemicals
