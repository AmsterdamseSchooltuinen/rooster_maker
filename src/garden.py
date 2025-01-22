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
    teacher_availability: dict
    school_availability: dict
    model: cp_model.CpModel = cp_model.CpModel()

    def make_group_teacher_time_slots_dict(self):
        """Create a dictionary for all possible combinations of group, teacher and time slot."""
        group_time_teacher_availability = {}
        groups = ["school_1", "school_2", "school_3"]
        time_slots = ["mon_1", "mon_2", "mon_3"]
        teachers = ["Floris", "Thomas", "Nils"]

        for group in groups:
            for time_slot in time_slots:
                for teacher in teachers:
                    group_time_teacher_availability[(group, time_slot, teacher)] = (
                        self.model.NewBoolVar(f"{group}_{time_slot}_{teacher}")
                    )

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
