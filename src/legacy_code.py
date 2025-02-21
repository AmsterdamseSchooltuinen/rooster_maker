import pandas as pd
from ortools.sat.python import cp_model

# Time slots
time_slots = [
    "maandag, 09.00 - 10.30",
    "maandag, 10.45 - 12.15",
    "maandag, 13.30 - 15.00",
    "dinsdag, 09.00 - 10.30",
    "dinsdag, 10.45 - 12.15",
    "dinsdag, 13.30 - 15.00",
    "woensdag, 09.00 - 10.30",
    "woensdag, 10.45 - 12.15",
    "donderdag, 09.00 - 10.30",
    "donderdag, 10.45 - 12.15",
    "donderdag, 13.30 - 15.00",
    "vrijdag, 09.00 - 10.30",
    "vrijdag, 10.45 - 12.15",
    "vrijdag, 13.30 - 15.00",
]


# Import the garden constraints
max_groups_per_slot = 2
aantal_tuintjes = 520

# Import the school data
df = pd.read_excel("Data.xlsx")
n_groups = df.shape[0]

# Read availability of schools
availability_groups = {}
for i in range(n_groups):
    g_id = int(df["periodeid"].iloc[i])
    availability_groups[g_id] = []
    for col in ["vrijveld2", "vrijveld3", "vrijveld4", "vrijveld5", "vrijveld6"]:
        value = df[col].iloc[i]
        if pd.isna(value):
            break
        else:
            availability_groups[g_id].append(value)

# Read amount of students per class
size_groups = {}
for i in range(n_groups):
    g_id = int(df["periodeid"].iloc[i])
    number_of_students = int(df["leerlingen"].iloc[i])
    size_groups[g_id] = [number_of_students]

# Read teacher availability
teacher_df = pd.read_csv("DRAFT_educator_input.csv")
teacher_availability = {}
for idx, row in teacher_df.iterrows():
    teacher_name = row["Medewerker"]
    teacher_availability[teacher_name] = {}
    for slot in time_slots:
        cell_value = row[slot] if slot in row else "U"  # default 'U' if missing
        teacher_availability[teacher_name][slot] = 1 if cell_value == "X" else 0

# Build the model
model = cp_model.CpModel()

# Create binary variables for group-slot assignment
assignment = {}
for group in availability_groups.keys():
    for slot in time_slots:
        assignment[(group, slot)] = model.NewBoolVar(f"shift_g{group}_s{slot}")

# Create binary variables for teacher-group-slot assignment
teacher_assignment = {}
for group in availability_groups.keys():
    for teacher in teacher_availability.keys():
        for slot in time_slots:
            teacher_assignment[(group, teacher, slot)] = model.NewBoolVar(
                f"ta_g{group}_t{teacher}_s{slot}"
            )

# Each group is scheduled at most once
for group in availability_groups.keys():
    model.Add(sum(assignment[(group, slot)] for slot in time_slots) <= 1)

# Max number of groups per time slot
for slot in time_slots:
    model.Add(
        sum(assignment[(group, slot)] for group in availability_groups)
        <= max_groups_per_slot
    )

# A group can only be assigned t o a slot if it's in their availability
for group, availability in availability_groups.items():
    for slot in time_slots:
        if slot not in availability:
            model.Add(assignment[(group, slot)] == 0)

# Total number of students must not exceed available plots
model.Add(
    sum(
        size_groups[group][0] * assignment[(group, slot)]
        for group in availability_groups.keys()
        for slot in time_slots
    )
    <= aantal_tuintjes
)

# Link group-slot assignment to teacher assignment:
# (1) If a group is assigned to a slot, at least one teacher must cover it
for group in availability_groups.keys():
    for slot in time_slots:
        model.Add(
            sum(
                teacher_assignment[(group, t, slot)]
                for t in teacher_availability.keys()
            )
            >= assignment[(group, slot)]
        )

# (2) If teacher_assignment is 1, then both the group and the teacher must be available
for group in availability_groups.keys():
    for teacher in teacher_availability.keys():
        for slot in time_slots:
            # teacher assignment cannot exceed the group's assignment
            model.Add(
                teacher_assignment[(group, teacher, slot)] <= assignment[(group, slot)]
            )
            # teacher assignment cannot exceed teacher availability
            if teacher_availability[teacher][slot] == 0:
                model.Add(teacher_assignment[(group, teacher, slot)] == 0)

# (3) Each teacher can only teach one group per slot
for teacher in teacher_availability.keys():
    for slot in time_slots:
        model.Add(
            sum(
                teacher_assignment[(g, teacher, slot)]
                for g in availability_groups.keys()
            )
            <= 1
        )

# Objective function
a = 0.005
model.Maximize(
    sum(
        assignment[(group, slot)]
        for group in availability_groups
        for slot in time_slots
    )
    + a
    * sum(
        assignment[(group, slot)]
        * (
            10
            if slot == availability_groups[group][0]
            else (
                5
                if len(availability_groups[group]) > 1
                and slot == availability_groups[group][1]
                else (
                    2
                    if len(availability_groups[group]) > 2
                    and slot == availability_groups[group][2]
                    else 0
                )
            )
        )
        for group in availability_groups
        for slot in time_slots
    )
)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print results
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print("Assignment:")
    for group in availability_groups.keys():
        assigned_slot = None
        for slot in time_slots:
            if solver.Value(assignment[(group, slot)]) == 1:
                assigned_slot = slot
                break
        if assigned_slot:
            # Determine which choice this slot was for the group
            try:
                choice_index = availability_groups[group].index(assigned_slot) + 1
            except ValueError:
                choice_index = "N/A"  # Shouldn't happen if constraints are correct
            # Find assigned teacher(s)
            assigned_teachers = []
            for teacher in teacher_availability.keys():
                if (
                    solver.Value(teacher_assignment[(group, teacher, assigned_slot)])
                    == 1
                ):
                    assigned_teachers.append(teacher)
            print(
                f"Group {group} -> Slot '{assigned_slot}' (Choice {choice_index}), "
                f"Teacher(s): {assigned_teachers if assigned_teachers else 'None'}"
            )
        else:
            print(f"Group {group} could not be assigned to any slot.")
else:
    print("No feasible solution found.")
