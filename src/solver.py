from ortools.sat.python import cp_model
from src.constraint_functions import add_constraints
from src.garden import Garden
from src.objective_function import add_objective_function
import time


def solve_schedule_problem(garden: Garden) -> tuple[cp_model.CpSolver, dict, bool]:
    """
    This function creates the garden's schedule by solving the optimization
    :param garden: contains all information about the garden such as its availability,
    capacity and the educator availability
    :type garden: Garden
    """
    # define and add the objective function

    # Initialize the model
    model = cp_model.CpModel()

    availability = make_group_teacher_time_slots_dict(garden, model)

    model = add_constraints(
        garden,
        model,
        availability,
    )

    add_objective_function(
        garden,
        model,
        availability,
    )

    # Solve the model
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10

    start = time.time()
    status = solver.Solve(model)
    print(f"Time: {time.time() - start:.2f} s")

    # Return results
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        solved_status = True
    else:
        solved_status = False

    return solver, availability, solved_status


def make_group_teacher_time_slots_dict(garden: Garden, model: cp_model.CpModel) -> dict:
    """Create a dictionary for all possible combinations of group, teacher and time slot."""
    group_time_teacher_availability = {}

    for group in garden.groups:
        for time_slot in garden.time_slots:
            for teacher in garden.teachers:
                group_time_teacher_availability[(group, time_slot, teacher)] = (
                    model.NewBoolVar(f"{group}_{time_slot}_{teacher}")
                )

    print("search space size:", len(group_time_teacher_availability))
    return group_time_teacher_availability


    for group in garden.groups:
        for time_slot in garden.time_slots:
            for teacher in garden.teachers:
                group_time_teacher_availability[(group, time_slot, teacher)] = (
                    model.NewBoolVar(f"{group}_{time_slot}_{teacher}")
                )

    print("search space size:", len(group_time_teacher_availability))
    return group_time_teacher_availability
