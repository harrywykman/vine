from sqlmodel import Session

from data.vineyard import GrowthStage
from database import engine

# Corrected E-L system growth stages data
growth_stages_data = [
    # Dormancy and Budbreak (EL 1-9)
    (1, "Winter bud"),
    (2, "Bud swell"),
    (3, "Woolly bud"),
    (4, "Green shoot visible"),
    (5, "First leaf unfolded"),
    (6, "Two to three leaves unfolded"),
    (7, "Four to five leaves unfolded"),
    (8, "Six to seven leaves unfolded"),
    (9, "Eight or more leaves unfolded"),
    # Shoot Development (EL 10-19)
    (10, "Shoot elongating rapidly"),
    (11, "Four to six leaves separated"),
    (12, "Inflorescence clearly visible"),
    (13, "Inflorescence well separated"),
    (14, "Flowers separating"),
    (15, "First flower caps loosened"),
    (16, "10% caps off"),
    (17, "30% caps off"),
    (18, "50% caps off"),
    (19, "80% caps off"),
    # Flowering (EL 20-29)
    (20, "First flower caps loosened"),
    (21, "10% caps off"),
    (22, "30% caps off"),
    (23, "50% caps off (full bloom)"),
    (24, "80% caps off"),
    (25, "Cap fall complete"),
    (26, "Young berries enlarging"),
    (27, "Young berries still hard and green"),
    (28, "Young berries softening"),
    (29, "Young berries still hard and green"),
    # Berry Development (EL 30-39)
    (30, "Berry set"),
    (31, "Berries pea-sized"),
    (32, "Berries begin to touch"),
    (33, "Berries still hard and green"),
    (34, "Berries still hard and green"),
    (35, "Berries begin to color and enlarge (veraison)"),
    (36, "Berries with intermediate sugar values"),
    (37, "Berries not quite ripe"),
    (38, "Berries ripe for harvest"),
    (39, "Berries over-ripe"),
    # Maturity and Senescence (EL 40-47)
    (40, "Berries over-ripe"),
    (41, "After harvest, canes mature"),
    (42, "Beginning of leaf fall"),
    (43, "End of leaf fall"),
    (44, "End of wood maturation"),
    (45, "End of leaf fall"),
    (46, "50% leaf fall"),
    (47, "End of leaf fall"),
]


def seed_growth_stages():
    """Seed the database with E-L system growth stages"""
    with Session(engine) as session:
        # Major phenological stages - key stages for viticulture
        major_stages = [
            1,  # Winter bud
            4,  # Green shoot visible
            5,  # First leaf unfolded
            10,  # Shoot elongating rapidly
            12,  # Inflorescence clearly visible
            15,  # First flower caps loosened
            23,  # 50% caps off (full bloom)
            31,  # Berries pea-sized
            32,  # Berries begin to touch
            35,  # Berries begin to color and enlarge (veraison)
            38,  # Berries ripe for harvest
            41,  # After harvest, canes mature
            43,  # End of leaf fall
            47,  # End of leaf fall
        ]

        for el, desc in growth_stages_data:
            # Check if stage already exists
            existing_stage = session.get(GrowthStage, el)

            if not existing_stage:
                stage = GrowthStage(
                    el_number=el, description=desc, is_major=el in major_stages or False
                )
                session.add(stage)
                print(
                    f"################ Added Growth Stage EL {el}: {desc} ################"
                )
            else:
                # Update existing stage with new description and is_major status
                existing_stage.description = desc
                existing_stage.is_major = el in major_stages or False
                session.add(existing_stage)
                print(
                    f"################ Updated Growth Stage EL {el}: {desc} ################"
                )

        session.commit()
        print(
            f"################ Successfully seeded {len(growth_stages_data)} growth stages ################"
        )


if __name__ == "__main__":
    seed_growth_stages()
