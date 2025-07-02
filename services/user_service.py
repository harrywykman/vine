import datetime
from typing import Optional

from passlib.handlers.sha2_crypt import sha512_crypt as crypto
from sqlalchemy import func
from sqlalchemy.future import select
from sqlmodel import Session, select

from data.user import User


def user_count(session: Session) -> int:
    query = select(func.count(User.id))
    result = session.exec(query)
    return result.all()


def create_account(
    session: Session, name: Optional[str], email: Optional[str], password: Optional[str]
) -> User:
    if not password:
        raise Exception("password is required")
    if not email:
        raise Exception("email is required")
    if not name:
        raise Exception("name is required")

    user = User()
    user.email = email
    user.name = name
    user.hash_password = crypto.hash(password, rounds=172_434)

    session.add(user)
    session.commit()

    return user


def login_user(session: Session, email: str, password: str) -> Optional[User]:
    query = select(User).filter(User.email == email)
    results = session.exec(query)

    user = results.one_or_none()
    if not user:
        return user

    try:
        if not crypto.verify(password, user.hash_password):
            return None
    except ValueError:
        return None

    # TODO update last_login
    user.last_login = datetime.datetime.now()
    session.add(user)
    session.commit()

    return user


def get_user_by_id(session, user_id: int) -> Optional[User]:
    return session.get(User, user_id)


"""     query = select(User).filter(User.id == user_id)
    result = session.exec(query)

    print(f"RESULT: {result.one_or_none()}--------------------------------------------")

    return result.one_or_none() """


def get_user_by_email(session: Session, email: str) -> Optional[User]:
    query = select(User).filter(User.email == email)
    result = session.exec(query)

    return result.one_or_none()
