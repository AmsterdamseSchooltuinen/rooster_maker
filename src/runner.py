import pandas as pd
from ortools.sat.python import cp_model

from src.garden import Garden
from src.solver import solve_schedule_problem

# from src.excel_output_formatter import create_excel_output


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

    for garden_name in unique_gardens:
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
        group_uses_bus = {}
        groups_that_go_together_with_bus_per_school = {}

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
            group_uses_bus[row["period_id"]] = (
                1 if row["transport_type"] == "bus" else 0
            )
            if row["transport_type"] == "bus":
                if row["school_id"] in groups_that_go_together_with_bus_per_school:
                    groups_that_go_together_with_bus_per_school[
                        row["school_id"]
                    ].append(row["period_id"])
                else:
                    groups_that_go_together_with_bus_per_school[row["school_id"]] = [
                        row["period_id"]
                    ]

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
            group_uses_bus=group_uses_bus,
            group_sizes=group_sizes,
            n_required_plots=n_required_plots,
            group_availability=group_availability,
            teacher_availability=teacher_availability,
            variable_teacher_availability=variable_teacher_availability,
            groups_that_go_together_with_bus_per_school=groups_that_go_together_with_bus_per_school,
        )

        # Solve the schedule problem
        solver_result, assignment, solved = solve_schedule_problem(current_garden)

        # Get the summary statistics and output
        summary_stats = get_summary_statistics(
            solver_result, current_garden, assignment, solved, current_educator_data
        )
        all_summary_stats[garden_name] = summary_stats
        # TODO: how go from the solver to the actual output data that we want?
        #output = format_output(current_garden, solver_result)

    all_summary_stats["Alle Tuinen Overzicht"] = combine_garden_stats(all_summary_stats)

    return all_summary_stats #, output


def format_output(garden: Garden, solver: cp_model.CpSolver):
    teachers = list(garden.teacher_availability.keys())
    groups = garden.groups
    time_slots = garden.time_slots
    tuinlocatie = garden.name
    assigned_groups = []
    # Dictionary for output assigned schools
    output_data = {"Tuinlocatie": [tuinlocatie] + [""] * (len(time_slots) - 1), "Tijdslot": time_slots}
    for teacher in teachers:
        inschrijfcode_list = []
        schoolname_list = []
        transport_list = []
        for time_slot in time_slots:
            group_assigned = ""
            for group in groups:
                #check if this works
                if solver.Value(assignment[(group, time_slot, teacher)]) == 1:
                    group_assigned = group
                    assigned_groups.append(group)
                    break
            inschrijfcode_list.append(group_assigned)
            if group_assigned:
                #find schoolname and transportation based on periodeid
                schoolname_list.append("")
                transport_list.append("")
            else:
                schoolname_list.append("")
                transport_list.append("")
        output_data[f"{teacher}"] = inschrijfcode_list
        output_data[f"Schoolnaam_{teacher}"] = schoolname_list
        output_data[f"Vervoer_{teacher}"] = transport_list
    # Convert the dictionary to a df
    df_assigned = pd.DataFrame(output_data)
    # DataFrame for unassigned groups
    df_unassigned = pd.DataFrame(columns=['Inschrijfcode', 'Schoolnaam', 'Vervoer'])
    unassigned_groups = list(set(groups) - set(assigned_groups))
    for group in unassigned_groups:
        #find schoolname and transportation based on periodeid
        schoolname = ""
        transportation = ""
        # Create a new DataFrame row and concatenate correctly
        new_row = pd.DataFrame([[group, schoolname, transportation]],
                               columns=['Inschrijfcode', 'Schoolnaam', 'Vervoer'])
        df_unassigned = pd.concat([df_unassigned, new_row], ignore_index=True)
    return df_assigned, df_unassigned


def get_summary_statistics(
    solved_info: cp_model.CpSolver,
    garden: Garden,
    assignment: dict,
    solved: bool,
    current_educator_data: pd.DataFrame,
):

    # If the garden has a feasible solution, create the summary_statistics dictionary
    if solved:
        summary = {}
        assigned_groups = []
        assigned_students = 0
        unassigned_groups = []
        unassigned_students = 0
        schedule = pd.DataFrame(index=garden.teachers, columns=garden.time_slots)
        schedule = schedule.fillna("")

        for group in garden.groups:
            for time in garden.time_slots:
                for teacher in garden.teachers:
                    if solved_info.Value(assignment[(group, time, teacher)]) == 1:
                        assigned_groups.append(group)
                        schedule.at[teacher, time] = (
                            f"{group} (size: {garden.group_sizes[group]}) (bus: {garden.group_uses_bus[group]})"
                        )
                        assigned_students += garden.group_sizes[group]

        unassigned_groups = set(garden.groups) - set(assigned_groups)
        for group in unassigned_groups:
            unassigned_students += garden.group_sizes[group]
        summary = {
            "assigned_groups": assigned_groups,
            "unassigned_groups": unassigned_groups,
            "assigned_students": assigned_students,
            "unassigned_students": unassigned_students,
            "schedule": schedule,
            "current_educator_data": current_educator_data,
            "available_plots": garden.available_plots,
            "reserved_plots": garden.reserved_plots,
            "teachers": garden.teachers,
        }

    else:
        # TODO: change this text to being in Dutch!
        summary = ("The scheduling problem could not be solved for this garden with the current "
                "input data and the current constraints. Please review the data and constraints and run again.")

    SHOW_LOGS = False
    if SHOW_LOGS:
        if len(unassigned_groups) > 0:
            print("WARNING UNASSIGNED GROUPS")
            for group in unassigned_groups:
                print(f"{group} size:{ garden.group_sizes[group]}")
            print()
        print("available plots", garden.available_plots_with_reserve)
        print("assigned students", assigned_students)
        print("max buses per slot", garden.max_buses_per_time_slot)
    return summary


def combine_garden_stats(all_summary_stats: dict) -> dict:
    """
    Combines the summary statistics of all gardens into one dictionary
    :param all_summary_stats: dictionary containing the summary statistics of all gardens
    :return: dictionary containing the combined summary statistics
    """
    all_gardens = list(all_summary_stats.keys())
    combined_stats = {
        "assigned_groups": [],
        "unassigned_groups": [],
        "assigned_students": 0,
        "unassigned_students": 0,
        "schedule": pd.DataFrame(),
        "current_educator_data": pd.DataFrame(),
        "available_plots": 0,
        "reserved_plots": 0,
        "teachers": [],
    }

    for garden in all_gardens:
        combined_stats["assigned_groups"].extend(
            all_summary_stats[garden]["assigned_groups"]
        )
        combined_stats["unassigned_groups"].extend(
            all_summary_stats[garden]["unassigned_groups"]
        )
        combined_stats["assigned_students"] += all_summary_stats[garden][
            "assigned_students"
        ]
        combined_stats["unassigned_students"] += all_summary_stats[garden][
            "unassigned_students"
        ]
        combined_stats["schedule"] = pd.concat(
            [combined_stats["schedule"], all_summary_stats[garden]["schedule"]]
        )
        combined_stats["current_educator_data"] = pd.concat(
            [
                combined_stats["current_educator_data"],
                all_summary_stats[garden]["current_educator_data"],
            ],
            axis=0,
        )
        combined_stats["available_plots"] += all_summary_stats[garden][
            "available_plots"
        ]
        combined_stats["reserved_plots"] += all_summary_stats[garden]["reserved_plots"]
        combined_stats["teachers"].extend(all_summary_stats[garden]["teachers"])

    return combined_stats
