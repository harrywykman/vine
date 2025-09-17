from sqlmodel import Session

from data.vineyard import GrowthStage
from database import engine

# Corrected E-L system growth stages data
growth_stages_data = [
    # Dormancy and Budbreak (EL 1-9)
    (1, "Winter bud"),
    (2, "Bud scales opening"),
    (3, "Woolly bud"),
    (4, "Budburst: leaf tips visible"),
    (7, "First leaf separated from shoot tip"),
    (9, "2 to 3 leaves separated; shoots 2-4 cm long"),
    (11, "4 leaves separated"),
    (
        12,
        "Shoots 10 cm. 5 leaves separated; shoots about 10cm long; inflorescence clear",
    ),
    (13, "6 leaves separated"),
    (14, "7 leaves separated"),
    (
        15,
        "8 leaves separated, shoot elongating rapidly; single flowers in compact groups",
    ),
    (16, "10 leaves separated"),
    (17, "12 leaves separated; inforescence well developed, single flower separated"),
    (
        18,
        "14 leaves separated; flower caps still in place, but cap colour fading from green",
    ),
    (
        19,
        "Flowering Begins. About 16 leaves separated; beginning of flowering (first flower caps loosened)",
    ),
    (20, "10 % caps off"),
    (21, "30% caps off"),
    (23, "Flowering. 17 to 20 leaves separated; 50% caps off"),
    (25, "80% caps off"),
    (26, "Cap fall complete"),
    (
        27,
        "Setting. Young berries enlarging (> 2 mm diameter), bunch at right angles to stem",
    ),
    (29, "Berries pepper-corn size (4 mm diameter); bunches tending downwards"),
    (31, "Berries pea size (7 mm diameter)"),
    (32, "Beginning of bunch closure, berries touching (if bunches are tight)"),
    (33, "Berries still hard and green"),
    (34, "Berries begin to soften; Sugar starts increasing"),
    (35, "Veraison. Berries begin to color and enlarge"),
    (36, "Berries with intermediate sugar values"),
    (37, "Berries not quite ripe"),
    (38, "Harvest. Berries harvest ripe"),
    (39, "Berries over-ripe"),
    (41, "After harvest, canes maturation complete"),
    (43, "Beginning of leaf fall"),
    (47, "End of leaf fall"),
]


def seed_growth_stages():
    """Seed the database with E-L system growth stages"""
    with Session(engine) as session:
        # Major phenological stages - key stages for viticulture
        major_stages = [
            4,
            12,
            19,
            23,
            27,
            31,
            35,
            38,
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
