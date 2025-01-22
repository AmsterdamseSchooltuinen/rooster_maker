from ortools.sat.python import cp_model
from constraint_functions import add_constraints
from src.garden import Garden


def solve_schedule_problem(garden: Garden):
    """
    This function creates the garden's schedule by solving the optimization
    :param garden: contains all information about the garden such as its availability,
    capacity and the educator availability
    :type garden: Garden
    """
    # define and add the objective function

    # Initialize the model
    model = cp_model.CpModel()

    group_time_teacher_availability = make_group_teacher_time_slots_dict(garden, model)
    add_constraints(garden)
    add_objective_function(garden, model, group_time_teacher_availability)

    # Solve the model
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Return results
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        return solver
    else:
        return solver
        # TODO: what happens if non-feasible solution?


def make_group_teacher_time_slots_dict(garden: Garden, model: cp_model.CpModel) -> dict:
    """Create a dictionary for all possible combinations of group, teacher and time slot."""
    group_time_teacher_availability = {}

    for group in garden.groups:
        for time in garden.time_slots:
            for teacher in garden.teachers:
                group_time_teacher_availability[(group, time, teacher)] = (
                    model.NewBoolVar(f"{group}_{time}_{teacher}")
                )

    return group_time_teacher_availability


def add_objective_function(garden: Garden, model: cp_model.CpModel, assignment: dict):
    model.Maximize(define_objective_function(garden, assignment))


def define_objective_function(garden: Garden, assignment: dict):
    # TODO: update the Objective function
    a = 0.005
    sum(
        assignment[(group, slot)]
        for group in garden.groups
        for slot in garden.time_slots
    )
    +a * sum(
        assignment[(group, slot)]
        * (
            10
            if slot == garden.availability_groups[group][0]
            else (
                5
                if len(garden.availability_groups[group]) > 1
                and slot == garden.availability_groups[group][1]
                else (
                    2
                    if len(garden.availability_groups[group]) > 2
                    and slot == garden.availability_groups[group][2]
                    else 0
                )
            )
        )
        for group in garden.groups
        for slot in garden.time_slots
    )
