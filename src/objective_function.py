from ortools.sat.python import cp_model
from src.garden import Garden

def number_of_allocations(garden: Garden, assignment: dict):
    return (
        assignment[(group, time, teacher)]
        for group in garden.groups
        for time in garden.time_slots
        for teacher in garden.teachers
    )

def number_of_preferred_allocations(garden: Garden, assignment: dict):
    first_choice_score = garden.objective["first_choice_score"]
    second_choice_score = garden.objective["second_choice_score"]
    third_choice_score = garden.objective["third_choice_score"]

    return (
        assignment[(group, time, teacher)]
        * (
            first_choice_score
            if time == garden.group_availability[group][0]
            else (
                second_choice_score
                if len(garden.group_availability[group]) > 1
                and time == garden.group_availability[group][1]
                else (
                    third_choice_score
                    if len(garden.group_availability[group]) > 2
                    and time == garden.group_availability[group][2]
                    else 0
                )
            )
        )
        for group in garden.groups
        for time in garden.time_slots
        for teacher in garden.teachers
    )


def add_objective_function(garden: Garden, model: cp_model.CpModel, assignment: dict):
    preferred_allocation_weight = garden.objective["preferred_allocation_weight"]
    model.Maximize(
        sum(number_of_allocations(garden, assignment))
        + sum(
            number_of_preferred_allocations(garden, assignment)   
        ) * preferred_allocation_weight
    )
