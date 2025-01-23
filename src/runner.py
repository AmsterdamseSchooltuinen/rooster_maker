import pandas as pd
from garden import Garden
from solver import solve_schedule_problem
from extract_transform_load import get_timeslots


def run_program(school_data: pd.DataFrame, garden_data: pd.DataFrame, educator_data: pd.DataFrame):
    """
    This function contains function calls to create the garden object,
    solve the scheduling and output the information to be displayed and exported
    :param school_data: dataframe containing the school data
    :param garden_data: dataframe containing the garden specific data
    :param educator_data: dataframe containing the educator availability
    :return: summary statistics and output table to be exported
    """

    unique_gardens = garden_data['garden_name'].unique()
    all_summary_stats = {}
    output = None
    for garden_name in unique_gardens:
        # Subset the data to only include data relevant to the current garden
        current_school_data = school_data.loc[garden_data['garden_name'] == garden_name]
        current_educator_data = educator_data.loc[garden_data['garden_name'] == garden_name]
        current_garden_data = garden_data.loc[garden_data['garden_name'] == garden_name]

        time_slots = get_timeslots(current_educator_data, ['garden_name', 'educator'])

        # Create the educator availability dictionaries
        teacher_availability = {}
        variable_teacher_availability = {}
        for _, teacher_row in current_educator_data.iterrows():
            available_mask = teacher_row.isin(["B", "V"])
            available_times = teacher_row[available_mask]
            variable_available_mask = teacher_row.isin(["V"])
            variable_available_times = teacher_row[variable_available_mask]
            teacher_availability[teacher_row["teacher"]] = list(available_times.index)
            variable_teacher_availability[teacher_row["teacher"]] = list(
                variable_available_times.index
            )

        current_garden = Garden(name=garden_name,
                                available_plots_with_reserve=current_garden_data['available_plots'],
                                reserved_plots=current_garden_data['reserved_plots'],
                                max_groups_per_time_slot=current_garden_data['max_groups_per_timeslot'],
                                max_buses_per_time_slot=current_garden_data['max_buses_per_timeslot'],
                                groups=list(current_school_data['group_id'].unique()),
                                school_of_group=dict(zip(current_school_data['group_id'],
                                                         current_school_data['school_id'])),
                                group_sizes=dict(zip(current_school_data['group_id'],
                                                     current_school_data['students'])),
                                n_required_plots=dict(zip(current_school_data['group_id'],
                                                          current_school_data['students']+2)),
                                group_availability=dict(zip(current_school_data['group_id'],
                                                            [current_school_data['preference_1'],
                                                             current_school_data['preference_2'],
                                                             current_school_data['preference_3'],
                                                             current_school_data['preference_4'],
                                                             current_school_data['preference_5']])),
                                time_slots=time_slots,
                                teachers=list(current_educator_data['educator'].unique()),
                                teacher_availability=teacher_availability,
                                variable_teacher_availability=variable_teacher_availability)

        # Solve the schedule problem
        solver_result = solve_schedule_problem(current_garden)

        # Get the summary statistics and output
        summary_stats = get_summary_statistics(solver_result, current_garden)
        all_summary_stats[garden_name] = summary_stats
        output = format_output(solver_result, current_garden)
    return all_summary_stats, output


def extract_garden_data(garden_data: pd.DataFrame):
    unique_gardens = garden_data['garden_name'].unique()
    return


def format_output(solved_info: Object, garden: Garden):
    # TODO: fill this function? Or import it from wherever it is now.
    return 1


def get_summary_statistics(solved_info: Object, garden: Garden):
    # Create the summary_statistics dictionary for the given garden
    summary = {}
    n_assigned_groups = 0
    assigned_students = 0  # TODO!
    for group in garden.groups:
        for slot in garden.time_slots:
            if solved_info.Value(assignment[(group, slot)]) == 1:
                n_assigned_groups += 1
    summary["available_plots"] = garden.available_plots
    summary["reserved_plots"] = garden.reserved_plots
    summary["total_groups"] = len(garden.group_sizes)
    summary["assigned_groups"] = n_assigned_groups
    summary["unassigned_groups"] = len(garden.group_sizes) - n_assigned_groups
    return summary
