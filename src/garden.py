from dataclasses import dataclass
from typing import Optional
from ortools.sat.python import cp_model
from src.configs.get_config import get_config


@dataclass
class Garden:
    """Class containing all relevant information about a garden."""

    name: str
    groups: list
    time_slots: list
    teachers: list
    # These are all the variables that we need to pass to the constraint functions
    teacher_availability: dict  # {teacher: [time_slot_1,time_slot_2 ]}
    variable_teacher_availability: dict  # {teacher: [time_slot_1,time_slot_2 ]} This is a subset of teacher_availability
    group_availability: dict  # {group: [time_slot_1,time_slot_2 ]}
    available_plots_with_reserve: int
    reservation_gardens: int
    available_plots: int  # just available_plots_with_reserve minus reservation gardens
    max_groups_per_time_slot: int
    max_buses_per_time_slot: int
    group_sizes: dict  # {group: size}
    needed_plots: dict  # {group: size+2} includes the demo plots
    school_of_group: dict  # {group: school}

    def _set_constraints(self, front_end_constraints: Optional[dict] = None) -> None:
        """Set the constraints for the garden."""
        constraints_config = get_config("constraints_config")

        # Only keep the constraints that are set to be included
        included_constraints = [
            key for key, value in constraints_config.items() if value.get("included")
        ]

        if front_end_constraints:
            # TODO: Implement the front-end constraints properly
            included_constraints.update(front_end_constraints)

        self.constraints = included_constraints
