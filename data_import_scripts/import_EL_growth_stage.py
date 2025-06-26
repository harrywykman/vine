from sqlmodel import Session, SQLModel

from data.vineyard import GrowthStage
from database import engine

growth_stages_data = [
    (1, "Winter bud"),
    (2, "Bud scales opening"),
    (3, "Woolly bud"),
    (4, "Green shoot visible"),
    (5, "First leaf unfolded"),
    (6, "Two leaves unfolded"),
    (7, "Three leaves unfolded"),
    (8, "Four leaves unfolded"),
    (9, "Five leaves unfolded"),
    (10, "Six or more leaves unfolded"),
    (11, "Shoot elongating rapidly"),
    (12, "Inflorescence clearly visible"),
    (13, "Inflorescence well separated"),
    (14, "Flowers separating"),
    (15, "First flower caps loosened"),
    (16, "10% caps off"),
    (17, "50% caps off (full bloom)"),
    (18, "End of flowering"),
    (19, "Fruit set"),
    (20, "Small berries, round and hard"),
    (21, "Berries pea-sized"),
    (22, "Berries begin to touch"),
    (23, "Beginning of bunch closure"),
    (24, "Bunch closed"),
    (25, "Veraison begins (berries begin to color and soften)"),
    (26, "Veraison complete"),
    (27, "Berries ripe for harvest"),
    (28, "Harvest"),
    (29, "Post-harvest"),
    (30, "End of leaf fall"),
    (31, "Dormancy begins"),
    (32, "Deep dormancy"),
]


def seed_growth_stages():
    with Session(engine) as session:
        for el, desc in growth_stages_data:
            stage = GrowthStage(
                el_number=el,
                description=desc,
                is_major=el
                in [1, 5, 12, 17, 19, 25, 27, 28, 30, 32],  # Marking key stages
            )
            if not session.get(GrowthStage, el):
                session.add(stage)
        session.commit()


if __name__ == "__main__":
    SQLModel.metadata.create_all(engine)
    seed_growth_stages()
