from src.garden import Garden
from ortools.sat.python import cp_model


def only_schedule_groups_when_they_are_available(
    garden: Garden, model: cp_model.CpModel, availability: dict
) -> cp_model.CpModel:
    """Only assign a group if they are available at that time."""
    for group in garden.groups:
        group_availability = garden.group_availability[group]
        for time in garden.time_slots:
            if time not in group_availability:
                for teacher in garden.teachers:
                    model.Add(availability[(group, time, teacher)] == 0)

    return model


def only_schedule_teachers_when_they_are_available(
    garden: Garden, model: cp_model.CpModel, availability: dict
) -> cp_model.CpModel:
    """Only assign a teacher if he/she is available at that time."""
    for teacher in garden.teachers:
        teacher_availability = garden.teacher_availability[teacher]
        for time in garden.time_slots:
            if time not in teacher_availability:
                for group in garden.groups:
                    model.Add(availability[(group, time, teacher)] == 0)

    return model


def each_group_max_once_per_week(
    garden: Garden, model: cp_model.CpModel, availability: dict
) -> cp_model.CpModel:
    """Each group can only be scheduled at most once per week."""
    for group in garden.groups:
        model.add_at_most_one(
            availability[(group, time, teacher)]
            for time in garden.time_slots
            for teacher in garden.teachers
        )

    return model


def max_number_of_groups_per_time_slot(
    garden: Garden, model: cp_model.CpModel, availability: dict
) -> cp_model.CpModel:
    """
    There cannot be more groups than the max available groups per time slot.
    So we check if the total active groups per time slot is less than or equal to the max groups per time slot.
    """
    for time in garden.time_slots:
        model.Add(
            sum(
                availability[(group, time, teacher)]
                for group in garden.groups
                for teacher in garden.teachers
            )
            <= garden.max_groups_per_time_slot
        )
    return model


def no_more_students_than_plots(
    garden: Garden, model: cp_model.CpModel, availability: dict
) -> cp_model.CpModel:
    """The total number of students must not exceed the available plots.
    This is the total for the whole week.
    """
    model.Add(
        sum(
            garden.needed_plots[group] * availability[(group, time, teacher)]
            for group in garden.groups
            for time in garden.time_slots
            for teacher in garden.teachers
        )
        <= garden.available_plots
    )
    return model


def each_educator_max_once_per_time_slot(
    garden: Garden, model: cp_model.CpModel, availability: dict
) -> cp_model.CpModel:
    """Each educator can only teach one group per time slot."""
    for teacher in garden.teachers:
        for time in garden.time_slots:
            model.add_at_most_one(
                availability[(group, time, teacher)] for group in garden.groups
            )
    return model


def educator_gets_one_slot_of_for_variable_availability(
    garden: Garden, model: cp_model.CpModel, availability: dict
) -> cp_model.CpModel:
    """Educators can define multiple hours of which 1 needs to be unavailable."""
    for teacher in garden.teachers:
        if teacher not in garden.variable_teacher_availability:
            continue

        variable_teacher_availability = garden.variable_teacher_availability[teacher]
        model.Add(
            sum(
                availability[(group, time, teacher)]
                for group in garden.groups
                for time in variable_teacher_availability
            )
            <= len(variable_teacher_availability) - 1
        )
    return model


# def max_buses_per_time_slot(
#     garden: Garden, model: cp_model.CpModel, availability: dict
# ) -> cp_model.CpModel:
#     return model

# def educator_needs_one_maintenance_slots(
#     garden: Garden, model: cp_model.CpModel, availability: dict
# ) -> cp_model.CpModel:
#     return model

# def bus_groups_of_same_school_go_together(
#     garden: Garden, model: cp_model.CpModel, availability: dict
# ) -> cp_model.CpModel:
#     return model


# def constraint(
#     garden: Garden, model: cp_model.CpModel, availability: dict
# ) -> cp_model.CpModel:
#     return model


CONSTRAINT_METHODS = {
    "only_schedule_groups_when_they_are_available": only_schedule_groups_when_they_are_available,
    "only_schedule_teachers_when_they_are_available": only_schedule_teachers_when_they_are_available,
    "each_group_max_once_per_week": each_group_max_once_per_week,
    "max_number_of_groups_per_time_slot": max_number_of_groups_per_time_slot,
    "no_more_students_than_plots": no_more_students_than_plots,
    "each_educator_max_once_per_time_slot": each_educator_max_once_per_time_slot,
    "educator_gets_one_slot_of_for_variable_availability": educator_gets_one_slot_of_for_variable_availability,
    # "max_buses_per_time_slot": max_buses_per_time_slot,
    # "educator_needs_one_maintenance_slots": educator_needs_one_maintenance_slots,
    # "bus_groups_of_same_school_go_together": bus_groups_of_same_school_go_together,
    # "constraint": constraint,
}


def add_constraints(
    garden: Garden, model: cp_model.CpModel, availability: dict
) -> cp_model.CpModel:
    """Add all constraints to the model and availability dictionary.

    Args:
        garden (Garden): Object containing all relevant information for the constraints
        model (cp_model.CpModel): The mode which will be solved
        availability (dict): A dictionary with (group, time, teacher) as keys and
            binary variables as values. 0 if the group is not available at that time for that teacher

    Returns:
        tuple[cp_model.CpModel, dict]: The updated model and availability dictionary
    """
    for constraint in garden.constraints:
        if constraint not in CONSTRAINT_METHODS:
            raise ValueError(f"Constraint {constraint} is not implemented.")
        model = CONSTRAINT_METHODS[constraint](garden, model, availability)

    return model
