from ortools.sat.python import cp_model
from constraint_functions import add_constraints
from schedule_config import time_slots  # TODO: read this from the input data?


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

    # Create the binary variables for group-slot assignment
    # TODO: update to new structure!
    assignment = {}
    for group in garden.availability_groups.keys():
        for slot in time_slots:
            assignment[(group, slot)] = model.NewBoolVar(f"shift_g{group}_s{slot}")

    # Create the binary variables for teacher-group-slot assignment
    # TODO: update to new structure!
    teacher_assignment = {}
    for group in garden.availability_groups.keys():
        for teacher in garden.teacher_availability.keys():
            for slot in time_slots:
                teacher_assignment[(group, teacher, slot)] = model.NewBoolVar(
                    f"ta_g{group}_t{teacher}_s{slot}"
                )

    add_constraints(garden)
    add_objective_function(garden, model, assignment)

    # Solve the model
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Return results
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        return solver
    else:
        return solver
        # TODO: what happens if non-feasible solution?


def add_objective_function(garden, model, assignment):
    model.Maximize(define_objective_function(garden, assignment))


def define_objective_function(garden, assignment):
    # TODO: update the Objective function
    a = 0.005
    sum(
        assignment[(group, slot)]
        for group in garden.availability_groups
        for slot in time_slots
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
        for group in garden.availability_groups
        for slot in time_slots
    )
