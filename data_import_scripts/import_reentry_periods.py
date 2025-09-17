from sqlmodel import Session

from data.vineyard import ReentryPeriod
from database import engine

# Reentry periods data
reentry_periods_data = [
    ("a", "Do not enter treated area until the spray has dried"),
    ("b", "8 hours"),
    ("c", "12 hours"),
    ("d", "1 day"),
    ("e", "1 to 16 days depending on vineyard activity being performed"),
    ("f", "1 to 34 days depending on vineyard activity being performed"),
    ("g", "2 days"),
    ("h", "4 days depending on vineyard activity being performed"),
    ("i", "4 to 23 days depending on vineyard activity being performed"),
    ("j", "5 days"),
    ("k", "5 to 23 days depending on vineyard activity being performed"),
    ("l", "6 days depending on vineyard activity being performed"),
    ("m", "7 days"),
    ("n", "8 days"),
    ("o", "12 days depending on vineyard activity being performed"),
    ("p", "9 to 24 days depending on vineyard activity being performed"),
    ("q", "9 to 27 days depending on vineyard activity being performed"),
    ("r", "15 to 33 days depending on vineyard activity being performed"),
    ("s", "12 to 32 days depending on the vineyard activity being performed"),
]


def seed_reentry_periods():
    """Seed the database with reentry periods"""
    with Session(engine) as session:
        for letter_code, description in reentry_periods_data:
            # Check if reentry period already exists by letter_code
            existing_period = (
                session.query(ReentryPeriod)
                .filter(ReentryPeriod.letter_code == letter_code)
                .first()
            )

            if not existing_period:
                period = ReentryPeriod(letter_code=letter_code, description=description)
                session.add(period)
                print(
                    f"################ Added Reentry Period {letter_code}: {description} ################"
                )
            else:
                # Update existing period with new description
                existing_period.description = description
                session.add(existing_period)
                print(
                    f"################ Updated Reentry Period {letter_code}: {description} ################"
                )

        session.commit()
        print(
            f"################ Successfully seeded {len(reentry_periods_data)} reentry periods ################"
        )


if __name__ == "__main__":
    seed_reentry_periods()
