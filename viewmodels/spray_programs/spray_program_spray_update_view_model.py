from decimal import Decimal
from typing import List, Optional

from sqlmodel import Session, select

from data.vineyard import (
    Chemical,
    GrowthStage,
    Spray,
    SprayChemical,
    SprayProgram,
    Target,
)
from services import vineyard_service
from viewmodels.shared.viewmodel import ViewModelBase


class SprayUpdateViewModel(ViewModelBase):
    def __init__(
        self,
        request,
        session: Session,
        spray_id: int,
        spray_program_id: Optional[int] = None,
    ):
        super().__init__(request, session)

        self.spray_id = spray_id
        self.spray_program_id = spray_program_id
        self.spray = None
        self.spray_program = None

        self.spray = session.get(Spray, spray_id)
        if not self.spray:
            self.set_error("Spray not found")
            return

        self.spray_program = session.get(SprayProgram, spray_program_id)
        if not self.spray_program:
            self.set_error("Spray program not found")
            return

        self.growth_stages: list = vineyard_service.all_growth_stages(session)
        statement = select(Chemical).order_by(Chemical.name)
        self.chemicals = session.exec(statement).all()
        self.targets = [target.value for target in Target]

    def update_spray(
        self,
        name: str,
        water_spray_rate_per_hectare: int,
        growth_stage_id: Optional[int],
        spray_program_id: int,
        chemical_ids: List[int],
        targets: List[str],
        concentration_factors: List[Decimal],
    ) -> bool:
        """
        Update the spray with the provided data.
        Lists are matched by index - chemical_ids[0] goes with targets[0] and concentration_factors[0].
        """

        if not self.spray:
            self.set_error("Spray not found")
            return

        if not self.spray_program:
            self.set_error("Spray Program not found")
            return

        try:
            # Validate growth stage exists if provided
            if growth_stage_id:
                growth_stage = self.session.get(GrowthStage, growth_stage_id)
                if not growth_stage:
                    self.set_error("Growth stage not found")
                    return

            # Update spray basic fields
            self.spray.name = name
            self.spray.water_spray_rate_per_hectare = water_spray_rate_per_hectare
            self.spray.growth_stage_id = growth_stage_id if growth_stage_id else None
            self.spray.spray_program_id = spray_program_id

            # Remove existing spray chemicals
            existing_spray_chemicals = self.session.exec(
                select(SprayChemical).where(SprayChemical.spray_id == self.spray_id)
            ).all()

            for spray_chemical in existing_spray_chemicals:
                self.session.delete(spray_chemical)

            self.session.flush()

            for chemical_id, target_value, concentration_factor in zip(
                chemical_ids, targets, concentration_factors
            ):
                if not chemical_id and target_value and concentration_factor:
                    self.set_error(
                        "Please fill out the chemical fields in full or remove."
                    )
                    return

                # Validate chemical exists
                chemical = self.session.get(Chemical, chemical_id)
                if not chemical:
                    self.set_error(f"Chemical with ID {chemical_id} not found")
                    return

                # Convert target string to Target enum
                target_enum = None
                if target_value:
                    try:
                        target_enum = Target(target_value)
                    except ValueError:
                        self.set_error(f"Invalid target: {target_value}")
                        return

                # Create new spray chemical
                spray_chemical = SprayChemical(
                    spray_id=self.spray_id,
                    chemical_id=chemical_id,
                    concentration_factor=concentration_factor,
                    target=target_enum,
                )
                self.session.add(spray_chemical)

            # Commit the transaction
            self.session.commit()
            self.session.refresh(self.spray)

            self.set_success(f"Spray '{name}' updated successfully")
            return

        except Exception as e:
            self.session.rollback()
            self.set_error(f"Error updating spray: {str(e)}")
            return
