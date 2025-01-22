from src.garden import Garden


def add_constraints(self, garden: Garden):
    for constraint in self.garden.constraints:
        garden.model.add(constraint)
    pass


def define_objective_function():
    pass


def solve_garden():
    pass
