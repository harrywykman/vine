# import_users.py
import json
import os

from sqlmodel import Session, select

from data.user import User, UserRole
from database import engine
from services import user_service


def load_user_data():
    """Load user data from .users.json file"""
    dotfile_path = ".users.json"

    if not os.path.exists(dotfile_path):
        raise FileNotFoundError(
            f"User data file '{dotfile_path}' not found. Please create it first."
        )

    try:
        with open(dotfile_path, "r") as f:
            user_data = json.load(f)
        return user_data
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in '{dotfile_path}': {e}")
    except Exception as e:
        raise Exception(f"Error reading '{dotfile_path}': {e}")


def import_new_users():
    try:
        user_data = load_user_data()
        print(f"Loaded {len(user_data)} users from .users.json")
    except Exception as e:
        print(f"Error loading user data: {e}")
        return

    with Session(engine) as session:
        for entry in user_data:
            # Validate required fields
            required_fields = ["name", "email", "password", "role"]
            if not all(field in entry for field in required_fields):
                print(f"Skipping invalid entry (missing required fields): {entry}")
                continue

            existing = session.exec(
                select(User).where(User.email == entry["email"])
            ).first()
            if existing:
                print(f"User with email: {entry['email']} already exists")
            else:
                try:
                    new_user = user_service.create_account(
                        session,
                        entry["name"],
                        entry["email"],
                        entry["password"],
                        UserRole(value=entry["role"]),
                    )
                    print(f"Added {new_user.name}")
                except Exception as e:
                    print(f"Error creating user {entry['email']}: {e}")


if __name__ == "__main__":
    import_new_users()
