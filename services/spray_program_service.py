from sqlmodel import Session, select

from data.vineyard import SprayProgram


def get_all_spray_programs(session: Session) -> list[SprayProgram]:
    statement = select(SprayProgram).order_by(SprayProgram.year)
    spray_program = session.exec(statement).all()
    return spray_program
