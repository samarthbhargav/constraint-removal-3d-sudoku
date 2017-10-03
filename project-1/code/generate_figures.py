import os

import cnf
import viz_cube
from experiment import Data, Experiment, PycoSatSolver


target_directory = "../images/"

if __name__ == '__main__':
    sudoku, givens, basename = Data.read_sudoku(9, "./puzzles/1.txt")
    
    experiments = {
        "all": [
            cnf.one_digit_per_cell,
            cnf.one_x_row,
            cnf.one_y_row,
            cnf.one_z_row,
            cnf.block_constraint
        ],
        # 3 combos
        "x_y_block": [
            cnf.one_digit_per_cell,
            cnf.one_x_row,
            cnf.one_y_row,
            cnf.block_constraint
        ],
        "x_z_block": [
            cnf.one_digit_per_cell,
            cnf.one_x_row,
            cnf.one_z_row,
            cnf.block_constraint
        ],
        "y_z_block": [
            cnf.one_digit_per_cell,
            cnf.one_y_row,
            cnf.one_z_row,
            cnf.block_constraint
        ],
        "x_y_z": [
            cnf.one_digit_per_cell,
            cnf.one_x_row,
            cnf.one_y_row,
            cnf.one_z_row
        ],
        # 2 Combos
        "x_y": [
            cnf.one_digit_per_cell,
            cnf.one_x_row,
            cnf.one_y_row
        ],
        "x_z": [
            cnf.one_digit_per_cell,
            cnf.one_x_row,
            cnf.one_z_row,
        ],
        "y_z": [
            cnf.one_digit_per_cell,
            cnf.one_y_row,
            cnf.one_z_row,
        ],
        "x_block": [
            cnf.one_digit_per_cell,
            cnf.one_x_row,
            cnf.block_constraint
        ],
        "y_block": [
            cnf.one_digit_per_cell,
            cnf.one_y_row,
            cnf.block_constraint
        ],
        "z_block": [
            cnf.one_digit_per_cell,
            cnf.one_z_row,
            cnf.block_constraint
        ],
        # Singles
        "x": [
            cnf.one_digit_per_cell,
            cnf.one_x_row
        ],
        "y": [
            cnf.one_digit_per_cell,
            cnf.one_y_row
        ],
        "z": [
            cnf.one_digit_per_cell,
            cnf.one_z_row
        ],
        "block": [
            cnf.one_digit_per_cell,
            cnf.block_constraint
        ]
    }

    for experiment_name, constraints in experiments.items():
        experiment = Experiment(9, "Image Generation", constraints,
                                "./puzzles/", PycoSatSolver(), None, "./results/")
        sudoku, statistics = experiment.run_one(sudoku, givens)

        viz_cube.save_slices(sudoku, experiment_name, "tests")

        print(statistics)

    viz_cube.plot_slice(sudoku, 0, 1, save_fig=os.path.join(target_directory, "example_orientation_0.png"))
    viz_cube.plot_slice(sudoku, 1, 1, save_fig=os.path.join(target_directory, "example_orientation_1.png"))
    viz_cube.plot_slice(sudoku, 2, 1, save_fig=os.path.join(target_directory, "example_orientation_2.png"))


