from dataclasses import dataclass
from typing import Optional
from ortools.sat.python import cp_model
from src.configs.get_config import get_config


@dataclass
class Garden:
    """Class containing all relevant information about a garden."""

    name: str
    available_plots: int
    number_of_classrooms: int
    number_of_max_buses: int
    groups: list
    time_slots: list
    teachers: list
    teacher_availability: dict
    school_availability: dict

    def _set_constraints(self, front_end_constraints: Optional[dict]) -> None:
        """Set the constraints for the garden."""
        constraints_config = get_config("constraints_config")

        # Only keep the contraints that are set to be included
        included_constraints = [
            key for key, value in constraints_config.items() if value.get("included")
        ]

        if front_end_constraints:
            # TODO: Implement the front-end constraints properly
            included_constraints.update(front_end_constraints)

        self.constraints = included_constraints
