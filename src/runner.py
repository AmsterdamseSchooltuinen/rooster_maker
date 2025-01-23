import pandas as pd
from ortools.sat.python import cp_model

from src.garden import Garden
from src.solver import solve_schedule_problem


def run_program(
    school_data: pd.DataFrame,
    garden_data: pd.DataFrame,
    educator_data: pd.DataFrame,
    time_slots: list,
):
    """
    This function contains function calls to create the garden object,
    solve the scheduling and output the information to be displayed and exported
    :param school_data: dataframe containing the school data
    :param garden_data: dataframe containing the garden specific data
    :param educator_data: dataframe containing the educator availability
    :return: summary statistics and output table to be exported
    """

    unique_gardens = garden_data["garden_name"].unique()
    all_summary_stats = {}
    output = None
    for garden_name in unique_gardens[:1]:
        print(garden_name)
        # Subset the data to only include data relevant to the current garden
        current_school_data = school_data.loc[school_data["garden_name"] == garden_name]
        current_educator_data = educator_data.loc[
            educator_data["garden_name"] == garden_name
        ]
        current_garden_data = garden_data.loc[garden_data["garden_name"] == garden_name]

        # Create the educator availability dictionaries
        teacher_availability = {}
        variable_teacher_availability = {}
        for _, teacher_row in current_educator_data.iterrows():
            available_mask = teacher_row.isin(["B", "V"])
            available_times = teacher_row[available_mask]

            variable_available_mask = teacher_row.isin(["V"])
            variable_available_times = teacher_row[variable_available_mask]

            teacher_availability[teacher_row["educator"]] = list(available_times.index)
            variable_teacher_availability[teacher_row["educator"]] = list(
                variable_available_times.index
            )

        # Create school availability dictionary
        group_availability = {}
        school_of_group = {}
        group_sizes = {}
        n_required_plots = {}
        for _, row in current_school_data.iterrows():
            group_availability[row["period_id"]] = [
                row["preference_1"],
                row["preference_2"],
                row["preference_3"],
                row["preference_4"],
                row["preference_5"],
            ]

            school_of_group[row["period_id"]] = row["school_id"]
            group_sizes[row["period_id"]] = row["students"]
            n_required_plots[row["period_id"]] = row["students"] + 2

        current_garden = Garden(
            name=garden_name,
            groups=[int(x) for x in current_school_data["period_id"].unique()],
            time_slots=time_slots,
            teachers=list(current_educator_data["educator"].unique()),
            available_plots_with_reserve=int(
                current_garden_data["available_plots"].values[0]
            ),
            reserved_plots=int(current_garden_data["reserved_plots"].values[0]),
            max_groups_per_time_slot=int(
                current_garden_data["max_groups_per_timeslot"].values[0]
            ),
            max_buses_per_time_slot=int(
                current_garden_data["max_buses_per_timeslot"].values[0]
            ),
            school_of_group=school_of_group,
            group_sizes=group_sizes,
            n_required_plots=n_required_plots,
            group_availability=group_availability,
            teacher_availability=teacher_availability,
            variable_teacher_availability=variable_teacher_availability,
        )

        # Solve the schedule problem
        solver_result, assignment = solve_schedule_problem(current_garden)

        # Get the summary statistics and output
        summary_stats = get_summary_statistics(
            solver_result, current_garden, assignment
        )
        all_summary_stats[garden_name] = summary_stats
        output = format_output(solver_result, current_garden)
    return all_summary_stats, output


def format_output(solved_info: cp_model.CpSolver, garden: Garden):
    # TODO: fill this function? Or import it from wherever it is now.
    return 1


def get_summary_statistics(
    solved_info: cp_model.CpSolver, garden: Garden, assignment: dict
):
    # Create the summary_statistics dictionary for the given garden
    summary = {}
    assigned_groups = []
    assigned_students = 0  # TODO!
    schedule = pd.DataFrame(index=garden.teachers, columns=garden.time_slots)
    schedule = schedule.fillna("")

    for group in garden.groups:
        for time in garden.time_slots:
            for teacher in garden.teachers:
                if solved_info.Value(assignment[(group, time, teacher)]) == 1:
                    assigned_groups.append(group)
                    schedule.at[teacher, time] = (
                        f"{group} ({garden.group_sizes[group]})"
                    )
                    assigned_students += garden.group_sizes[group]

    # Some log information

    unasigned_groups = set(garden.groups) - set(assigned_groups)
    display(schedule)
    print("Unassigned groups:", unasigned_groups)
    print(f"max_groups_per_time_slot: {garden.max_groups_per_time_slot}")
    print(f"max_buses_per_time_slot: {garden.max_buses_per_time_slot}")
    print(f"available_plots: {garden.available_plots}")
    print(f"assigned_students: {assigned_students}")

    summary["available_plots"] = garden.available_plots
    summary["reserved_plots"] = garden.reserved_plots
    summary["total_groups"] = len(garden.group_sizes)
    summary["assigned_groups"] = len(set(assigned_groups))
    summary["unassigned_groups"] = len(unasigned_groups)
    print(summary)
    return summary
