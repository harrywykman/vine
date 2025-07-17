# import_users.py

from sqlmodel import Session, select

from data.user import User, UserRole
from database import engine
from services import user_service

# The data to insert or update
user_data = [
    {
        "name": "Harry",
        "email": "hello@harrywykman.com",
        "password": "password",
        "role": "operator",
    },
    {
        "name": "Colin",
        "email": "colin@ahaviticulture.com.au",
        "password": "password",
        "role": "admin",
    },
    {
        "name": "Nic",
        "email": "nic@ahaviticulture.com.au",
        "password": "password",
        "role": "operator",
    },
    {
        "name": "Larissa",
        "email": "larissa@ahaviticulture.com.au",
        "password": "password",
        "role": "admin",
    },
]


def import_new_users():
    with Session(engine) as session:
        for entry in user_data:
            existing = session.exec(
                select(User).where(User.email == entry["email"])
            ).first()

            if existing:
                print(f"User with email: {entry['email']} already exists")
            else:
                new_user = user_service.create_account(
                    session,
                    entry["name"],
                    entry["email"],
                    entry["password"],
                    UserRole(value=entry["role"]),
                )
                print(f"Added {new_user.name}")


if __name__ == "__main__":
    import_new_users()
