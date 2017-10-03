import os
import time
import timeout_decorator
from enum import Enum

import pycosat
import numpy as np
import pandas as pd

import cnf
from output_grabber import OutputGrabber 

def _log(*args, verbose=True):
    if verbose:
        print(*args)

class Constraints(Enum):
    X = 0
    Y = 0
    Z = 0
    BLOCK = 0


class SatSolver:
    def __init__(self):
        raise NotImplementedError()

    def solve(self, clauses, metrics = None):
        raise NotImplementedError()

class PycoSatSolver(SatSolver):
    def __init__(self):
        self.p = pycosat

    def solve(self, clauses, metrics = None):
        if metrics:
            # TODO Capture STDOUT and parse the output
            pass

        with OutputGrabber() as grabber:
            solution = self.p.solve(clauses, verbose=1)
        
        stats = grabber.capturedtext

        if solution == "UNSAT":
            return RunResult.UNSAT, None
        return RunResult.SAT, solution, stats

class Data:

    @staticmethod
    def read_sudoku(size, file_name):
        sudoku = np.zeros((size, size, size))
        givens = []
        with open(file_name) as reader:
            for line in reader:
                x, y, z, val = line.strip().split(",")
                x, y, z = int(x), int(y), int(z)
                sudoku[x, y, z] = int(val) - 1
                # -1 because we're using givens with 0-8
                givens.append([cnf.spatial_to_dimacs(size, x, y, z, int(val)-1)])

        return sudoku, givens, os.path.basename(file_name)

    @staticmethod
    def sudoku_iterator(size, data_directory):
        for file_name in os.listdir(data_directory):
            yield Data.read_sudoku(size, os.path.join(data_directory, file_name))

class RunResult(Enum):
    SAT = 0
    UNSAT = 1
    TIME_OUT = 2

class Experiment:

    def __init__(self, size, experiment_name, constraints, data_directory, sat_solver, metrics, stats_directory):
        self.size = size
        self.constraints = constraints
        self.data_directory = data_directory
        self.number_of_puzzles = len(os.listdir(data_directory))
        self.sat_solver = sat_solver
        self.metrics = metrics
        self.experiment_name = experiment_name
        self.stats_directory = stats_directory
        
        self.common_clauses = cnf.encode_sudoku_with_constraints(self.size, 
                cnf.naive_exactly_one, constraints=self.constraints)
        self.killed = 0

    def run(self):

        def solve(sat_solver, clauses, metrics):
            return sat_solver.solve(clauses, metrics)

        @timeout_decorator.timeout(5, use_signals=False)
        def solve_single_puzzle(sat_solver, clauses, metrics):
            run_result, solution, statistics = solve(self.sat_solver, clauses, self.metrics)
            return run_result, solution, statistics

        _log("Running experiment: {}".format(self.experiment_name))
        _log("Found {} puzzles".format(self.number_of_puzzles))

        for index, (sudoku, givens, sudoku_name)  in enumerate(Data.sudoku_iterator(self.size, self.data_directory)):
            if index % 10 == 0:
                _log("\tRunning puzzle {} of {}".format(index + 1, self.number_of_puzzles))
            clauses = self.common_clauses[:] 
            clauses.extend(givens)
            start_time = time.time()
            
            try:
                run_result, solution, statistics = solve_single_puzzle(self.sat_solver, clauses, self.metrics)
            except timeout_decorator.timeout_decorator.TimeoutError as e:
                print(e)
                run_result = RunResult.TIME_OUT


            if run_result == RunResult.UNSAT:
                raise ValueError("Encountered an unsatisfiable sudoko")

            if run_result == RunResult.TIME_OUT:
                # figure out how to handle this!
                print("Unable to solve puzzle {} within timelimit, skipping. ".format(index + 1))
                self.killed += 1
                continue

            self.save_statistics(statistics, sudoku_name)

            # filter out negations
            solution = filter(lambda _: _ > 0, solution)
            
            for dimac in solution:
                x, y, z, digit = cnf.dimacs_to_spatial(self.size, dimac)
                sudoku[x, y, z] = digit

            _log("Solved puzzle {} of {}. Took {} seconds".format(index + 1, self.number_of_puzzles, time.time() - start_time))


        _log("Finished running all {} puzzles".format(self.number_of_puzzles))
        # Now write number killed
        with open("{}{}_killed".format(self.stats_directory, self.experiment_name), "w") as results_file:
            results_file.write(self.killed)
            results_file.close()

    def run_one(self, sudoku, givens):

        def solve(sat_solver, clauses, metrics):
            return sat_solver.solve(clauses, metrics)


        clauses = self.common_clauses[:] 
        clauses.extend(givens)

        start_time = time.time()
            
        run_result, solution, statistics = solve(self.sat_solver, clauses, self.metrics)

        if run_result in {RunResult.UNSAT, RunResult.TIME_OUT}:
            raise ValueError("Encountered an unsatisfiable sudoku")

        # filter out negations
        solution = filter(lambda _: _ >= 0, solution)

        for dimac in solution:
            x, y, z, digit = cnf.dimacs_to_spatial(self.size, dimac)
            sudoku[x, y, z] = digit

        _log("Solved puzzle. Took {} seconds".format(time.time() - start_time))

        return sudoku, statistics


    def save_statistics(self, statistics, sudoku_name):
        with open("{}{}_{}".format(self.stats_directory, self.experiment_name, sudoku_name), "w") as results_file:
            results_file.write(statistics)
            results_file.close()


if __name__ == '__main__':
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
        ],
    }

    for experiment_name, constraints in experiments.items():
        experiment = Experiment(9, experiment_name, constraints,
                                "./puzzles/", PycoSatSolver(), None, "./results/")
        experiment.run()    
