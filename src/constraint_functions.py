from src.garden import Garden


def add_constraints(garden: Garden):
    for constraint in garden.constraints:
        if constraint == "constraint1":
            add_constraint1(garden)
        elif constraint == "constraint2":
            add_constraint2(garden)
        # elif constraint == "constraint3":
        #     add_constraint3(garden)
        # elif constraint == "constraint4":
        #     add_constraint4(garden)
        # etc...
    add_constraint1(garden)
    add_constraint2(garden)
    # etc...
    return


def add_constraint1(garden: Garden):
    return


def add_constraint2(garden: Garden):
    return
