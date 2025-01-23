import pandas as pd
from garden import Garden
from solver import solve_schedule_problem
from somewhere import get_summary_statistics
# TODO: change the import to be real


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

        # TODO: extract the teacher availability based on the value of each column
        # TODO: determine the format of the availability of groups, teachers and timeslots

        current_garden = Garden(name=garden_name,
                                available_plots=current_garden_data['available_plots'],
                                number_of_classrooms=current_garden_data['max_groups_per_timeslot'],
                                number_of_max_buses=current_garden_data['max_buses_per_timeslot'],
                                group_availability=dict(zip(current_school_data['group_id'],
                                                            [current_school_data['preference_1'],
                                                             current_school_data['preference_2'],
                                                             current_school_data['preference_3'],
                                                             current_school_data['preference_4'],
                                                             current_school_data['preference_5']])),
                                time_slots=[1],
                                teachers=list(current_educator_data['educator'].unique()),
                                teacher_availability=dict(zip(current_educator_data['educator'],
                                                              [current_educator_data['preference_1'],
                                                               current_educator_data['preference_2'],
                                                               current_educator_data['preference_3'],
                                                               current_educator_data['preference_4'],
                                                               current_educator_data['preference_5']])))

        # Solve the schedule problem
        solver_result = solve_schedule_problem(current_garden)

        # Get the summary statistics and output
        summary_stats = get_summary_statistics(solver_result)
        all_summary_stats[garden_name] = summary_stats
        output = format_output(solver_result)
    return all_summary_stats, output


def extract_garden_data(garden_data: pd.DataFrame):
    unique_gardens = garden_data['garden_name'].unique()
    return


def format_output(solved_info: Object):
    # TODO: fill this function? Or import it from wherever it is now.
    return 1


