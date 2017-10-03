import numpy as np
import itertools
from math import sqrt

# TODO: Extract construction of puzzle to separate file


def generate_dimacs_in_ranges(n,
                              x_values,
                              y_values,
                              z_values,
                              digit_values):
    """Generate DIMACS values for spatial digits with ranges
    (no specific tuple-wise combinations)"""
    prop_variables = []
    # First generate the set of propositional variables
    for x in x_values:
        for y in y_values:
            for z in z_values:
                for d in digit_values:
                    prop_variables.append(
                        spatial_to_dimacs(n, x, y, z, d)
                    )
    return prop_variables


def generate_clauses_blocks_in_slice(n,
                                     z_index,
                                     exactly_one_function):
    clauses = []
    for block in range(n):
        square_root = int(sqrt(n))
        block_row = int(block / square_root)*square_root
        block_col = int(block % square_root)*square_root
        for digit in range(n):
            prop_variables = [spatial_to_dimacs(n=n, digit=digit, x=block_row+i, y=block_col+j, z=z_index)
                              for i in range(square_root) for j in range(square_root)]
            """"
            for row_pos in range(square_root):
                for col_pos in range(square_root):
                    row = block_row + row_pos
                    column = block_col + col_pos
                    prop_variables.append(spatial_to_dimacs(
                        **dimacs_args(digit, row, column)
                    ))
                    """
            clauses.extend(exactly_one_function(prop_variables))

    return clauses


def naive_exactly_one(prop_variables):
    """Naive Exactly One Algorithm"""
    # Then generate the clauses!
    naive_at_least_one = prop_variables
    naive_combination = (-1 * np.array([list(x) for x in itertools.combinations(prop_variables, 2)])).tolist()
    naive_combination.append(naive_at_least_one)
    return naive_combination


def spatial_to_dimacs(n, x, y, z, digit):
    """Converts the spatial coordinates and digit position to the
        corresponding DIMACS variable. N.B.!!! They must start at 0
        The offsets are calculated with respect to the
        digits first, then x, then y, then z, so that the conversion is
        n^3*+n^2*y+n*x+d+1
        """
    return (n**3)*z+(n**2)*y+n*x+digit+1


def dimacs_to_spatial(n, dimacs_value):
    assert dimacs_value <= n**4 + 1

    def d_prime_and_value(n, d):
        value = d % n
        d_prime = (d - value) / n
        return int(value), int(d_prime)

    digit, d_prime = d_prime_and_value(n, dimacs_value - 1)
    x_value, d_prime = d_prime_and_value(n, d_prime)
    y_value, z_value = d_prime_and_value(n, d_prime)

    return x_value, y_value, z_value, digit + 1


# DIMACS File Interop
def to_dimacs(file_name, clauses, number_of_variables):
    """
    Write current collection of clauses to file in DIMACS format.
    """
    if file_name is None:
        print("Please enter a filename")
        return
    dimacs_file = open(file_name, "w")

    dimacs_file.write("p cnf {!s} {!s}\n".
                      format(number_of_variables, len(clauses)))

    # Icky impure func for writing a clause to DIMACS
    def write_clause(clause):
        """
        Write single clause in DIMACS format to file
        """
        dimacs_file.write(" ".join(map(str, clause)) + " 0\n")

    for clause in clauses:
        write_clause(clause)
    dimacs_file.close()


def from_dimacs(filename):
    dimacs_file = open(filename)
    clauses = [[int(n) for n in line.split() if n != '0'] for line in dimacs_file if line[0] not in ('c', 'p')]
    dimacs_file.close()
    return clauses


def sudoku_givens_to_clauses(filename):
    sudoku_file = open(filename)
    n = int(sudoku_file.readline().split()[1])
    givens = []
    cube = np.zeros((n, n, n), dtype=int)
    for row, line in enumerate(sudoku_file):
        givens_line = line.split()
        additional_givens = []
        for column, value in enumerate(givens_line):
            if int(value) != -1:
                x = row % n
                y = column
                z = row // n
                digit = int(value)
                additional_givens.append([spatial_to_dimacs(n, x, y, z, digit)])
                cube[x][y][z] = digit
        givens.extend(additional_givens)
    return givens, cube


# ##### Sudoku constraints as functions #####
def range_constraint(n, encoding_strategy, kwarg_gen):
    constraints = []
    for i in range(n):
        for j in range(n):
            for k in range(n):
                constraints.extend(encoding_strategy(
                    generate_dimacs_in_ranges(**kwarg_gen(i, j, k))
                ))
    return constraints


# Exactly one d per cell
def one_digit_per_cell(n, encoding_strategy):
    constraints = []
    for row in range(n):
        for column in range(n):
            for z in range(n):
                constraints.extend(encoding_strategy(
                    generate_dimacs_in_ranges(n=n,
                                              x_values=[row],
                                              y_values=[column],
                                              z_values=[z],
                                              digit_values=range(n))
                ))
    print(len(constraints))
    return constraints
    """"
    return range_constraint(n, encoding_strategy,
                            lambda i, j, k: {
                                "n": n,
                                "x_values": [i],
                                "y_values": [j],
                                "z_values": [k],
                                "digit_values": range(n)
                            })
                            """


# Exactly one y_row where value is true
def one_y_row(n, encoding_strategy):
    return range_constraint(n, encoding_strategy,
                            lambda i, j, k: {
                                "n": n,
                                "x_values": [i],
                                "y_values": range(n),
                                "z_values": [j],
                                "digit_values": [k]
                            })


# Exactly one z_row where value is true
def one_z_row(n, encoding_strategy):
    return range_constraint(n, encoding_strategy,
                            lambda i, j, k: {
                                "n": n,
                                "x_values": [i],
                                "y_values": [j],
                                "z_values": range(n),
                                "digit_values": [k]
                            })


# Exactly one x_row where value is true
def one_x_row(n, encoding_strategy):
    return range_constraint(n, encoding_strategy,
                            lambda i, j, k: {
                                "n": n,
                                "x_values": range(n),
                                "y_values": [i],
                                "z_values": [j],
                                "digit_values": [k]
                            })


# Block constraint in x,y plane
def block_constraint(n, encoding_strategy):
    clauses = []
    for z in range(n):
        clauses.extend(generate_clauses_blocks_in_slice(n, z, encoding_strategy))

    return clauses


def encode_sudoku_with_constraints(n, exactly_one_function, constraints=None):
    if constraints is None:
        constraints=[
            one_digit_per_cell,
            one_y_row,
            one_x_row,
            one_z_row,
            block_constraint
        ]
    clauses = []
    for constraint in constraints:
        constraint_clauses = constraint(n, exactly_one_function)
        clauses.extend(constraint_clauses)
    return clauses

def read_scraped_cube(file_name):
    sudoku = np.zeros((9, 9, 9), dtype=int)
    givens = []
    with open(file_name) as reader:
        for line in reader:
            x, y, z, val = line.strip().split(",")
            x, y, z = int(x), int(y), int(z)
            sudoku[x, y, z] = int(val)-1
            givens.append([spatial_to_dimacs(9, x, y, z, int(val)-1)])
    return givens, sudoku

if __name__ == "__main__":
    side_length = 9
    clauses = encode_sudoku_with_constraints(side_length, naive_exactly_one,
                                             constraints=[
                                                 one_digit_per_cell,
                                                 one_x_row,
                                                 one_y_row,
                                                 one_z_row,
                                                 block_constraint
                                             ])
    import os
    dir_path = os.path.dirname(os.path.realpath(__file__))
    print(len(clauses))
    givens, cube = read_scraped_cube(dir_path + "/5349.txt")
    print(givens)
    clauses.extend(givens)
    import pycosat
    solution = pycosat.solve(clauses)
    print(solution)
    dimacs_solutions = filter(lambda _: _ > 0, solution)

    for dimac in dimacs_solutions:
        x, y, z, digit = dimacs_to_spatial(9, dimac)
        cube[x][y][z] = digit

    import viz_cube
    viz_cube.plot_slice(cube, 2, 1)
    # Saving stuff
    #CNF3D.to_dimacs(dir_path + "/cnf/4cubed.cnf", clauses, 4**4)




