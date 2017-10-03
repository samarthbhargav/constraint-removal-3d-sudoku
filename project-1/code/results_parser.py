import os
import re
import pickle
import pandas as pd

def picosat_file_parser(file):
    pico_stats_names = [
        "satisfiable",
        "seconds",
        "level",
        "variables",
        "used",
        "original",
        "conflicts",
        "learned",
        "limit",
        "agility",
        "MB"
    ]
    with open(file, "r") as pico_file:
        actual_stats_line = re.split(r"\s+", pico_file.readlines()[-1])[1:-1]
    actual_stats = list(map(lambda a: float(a), actual_stats_line))
    stats_map = dict(zip(pico_stats_names, actual_stats))
    return stats_map


class ResultsParser:
    def __init__(self, directory, statistics_file_parser):
        self.directory = directory
        self.file_parser = statistics_file_parser
        self.file_to_constraints_and_name = re.compile(r"^(.*)_(\d+).txt$")

    def get_puzzle_and_constraints(self, file_name):
        match = self.file_to_constraints_and_name.fullmatch(file_name)
        if match is None:
            print("Encountered file {} which isn't parseable".format(file_name))
            return None, None
        constraints, sudoku_name = match.groups()
        return sudoku_name, constraints

    def get_results(self):
        puzzle_results = []
        for index, file_name in enumerate(os.listdir(self.directory)):

            if index % 1000 == 0:
                print(index, " done")

            sudoku_name, constraints = self.get_puzzle_and_constraints(file_name)
            if sudoku_name is None:
                continue
            file_path = os.path.join(self.directory, file_name)
            file_stats = picosat_file_parser(file_path)
            #if puzzle_results.get(sudoku_name) is None:
            #    puzzle_results[sudoku_name] = {}
            #puzzle_results[sudoku_name][constraints] = file_stats
            file_stats["sudoku"] = sudoku_name
            file_stats["constraints"] = constraints
            puzzle_results.append(file_stats)

        results = pd.DataFrame(puzzle_results)
            
        return results


if __name__ == "__main__":
    picosat_results = ResultsParser("./results/", picosat_file_parser).get_results()

    picosat_results.to_csv("results.csv", index=False)

    pickle.dump(picosat_results, open("./pico_results", "wb"))
