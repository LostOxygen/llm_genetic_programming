"""main hook for the project"""
import os
import psutil
import datetime
import getpass
import torch
import numpy as np
import argparse
import matplotlib.pyplot as plt

from utils.colors import TColors
from ga.population import Population
from ga.algorithm import GeneticAlgorithm

def main(
        device: str,
        num_vars: int,
        pop_size: int,
        selection_size: int,
        init_depth: int,
        max_depth: int,
        train_iterations: int
    ) -> None:
    """
    Main function to run the project.

    Parameters:
        device (str): device to run the computations on (cpu, cuda, mps)
        num_vars (int): number of variables/terminals
        pop_size (int): population size
        selection_size (int): selection size to select father/mother from the population
        init_depth (int): initial depth of the tree for the chromosomes
        max_depth (int): maximum depth of the tree for the chromosomes
        train_iterations (int): number of training iterations
    """

    # set the devices correctly
    if device == "cpu":
        device = torch.device("cpu")
    elif device != "cpu" and device == "cuda" and torch.cuda.is_available():
        device = torch.device(device)
    elif device != "cpu" and device == "mps" and torch.backends.mps.is_available():
        device = torch.device(device)
    else:
        print(f"{TColors.WARNING}Warning{TColors.ENDC}: Device {TColors.OKCYAN}{device} " \
              f"{TColors.ENDC}is not available. Setting device to CPU instead.")
        device = torch.device("cpu")

    print("\n"+f"## {TColors.BOLD}{TColors.HEADER}{TColors.UNDERLINE}System Information" + \
          f"{TColors.ENDC} " + "#"*(os.get_terminal_size().columns-23))
    print(f"## {TColors.OKBLUE}{TColors.BOLD}Date{TColors.ENDC}: " + \
          str(datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p")))
    print(f"## {TColors.OKBLUE}{TColors.BOLD}System{TColors.ENDC}: " \
          f"{torch.get_num_threads()} CPU cores with {os.cpu_count()} threads and " \
          f"{torch.cuda.device_count()} GPUs on user: {getpass.getuser()}")
    print(f"## {TColors.OKBLUE}{TColors.BOLD}Device{TColors.ENDC}: {device}")
    if device == "cuda" and torch.cuda.is_available():
        print(f"## {TColors.OKBLUE}{TColors.BOLD}GPU Memory{TColors.ENDC}: " \
              f"{torch.cuda.mem_get_info()[1] // 1024**2} MB")
    elif device == "mps" and torch.backends.mps.is_available():
        print(f"## {TColors.OKBLUE}{TColors.BOLD}Shared Memory{TColors.ENDC}: " \
              f"{psutil.virtual_memory()[0] // 1024**2} MB")
    else:
        print(f"## {TColors.OKBLUE}{TColors.BOLD}CPU Memory{TColors.ENDC}: " \
              f"{psutil.virtual_memory()[0] // 1024**2} MB")
    print(f"## {TColors.BOLD}{TColors.HEADER}{TColors.UNDERLINE}Parameters" + \
          f"{TColors.ENDC} " + "#"*(os.get_terminal_size().columns-14))
    print(f"## {TColors.OKBLUE}{TColors.BOLD}Num. of Variables/Terminals{TColors.ENDC}: {num_vars}")
    print(f"## {TColors.OKBLUE}{TColors.BOLD}Population Size{TColors.ENDC}: {pop_size}")
    print(f"## {TColors.OKBLUE}{TColors.BOLD}Selection Size{TColors.ENDC}: {selection_size}")
    print(f"## {TColors.OKBLUE}{TColors.BOLD}Initial Depth{TColors.ENDC}: {init_depth}")
    print(f"## {TColors.OKBLUE}{TColors.BOLD}Maximum Depth{TColors.ENDC}: {max_depth}")
    print(f"## {TColors.OKBLUE}{TColors.BOLD}Training Iterations{TColors.ENDC}: {train_iterations}")
    print("#"*os.get_terminal_size().columns)

    print(f"{TColors.OKCYAN}[INFO]{TColors.ENDC}: " + \
          "Defining functions, variables/terminals, and targets")
    # define functions and terminals (variables of the functions)
    functions = {
        1: ["sin", "cos", "e", "ln", "tg", "tanh", "abs"],
        2: ["+", "-", "*", "/"],
    }
    terminals = ["x"+str(i) for i in range(num_vars)]

    # define the target function
    def target_func(x: float) -> float:
        result = 0.1 * x**2 * np.sin(x)

        if np.isinf(result):
            return 1e10
        elif np.isnan(result):
            return 0
        return result

    print(f"{TColors.OKCYAN}[INFO]{TColors.ENDC}: Creating input and label data")
    # create input and label data
    inputs = [[x] for x in np.arange(-50, 50, 0.001)]
    labels = [[target_func(x[0])] for x in inputs]

    print(f"{TColors.OKCYAN}[INFO]{TColors.ENDC}: Initializing the population")
    # initialize the population
    pop = Population(pop_size, selection_size, functions, terminals, init_depth, max_depth)

    # create and train the genetic algorithm
    algo = GeneticAlgorithm(pop, train_iterations, inputs, labels)
    best = algo.train()

    print(f"{TColors.OKCYAN}[INFO]{TColors.ENDC}: Getting predictions and plotting the results")
    # get predictions and plot the results
    print(f"{TColors.OKCYAN}[INFO]{TColors.ENDC} Best Gen: "+ str(best.gen))
    predictions = [[best.evaluate_arg(x)] for x in inputs]

    with plt.xkcd():
        plt.plot(inputs, labels, color="b", dashes=[6, 2], label="target function")
        plt.plot(inputs, predictions, color="r", dashes=[6, 3], label="predicted function")
        plt.legend()
        plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="llm-genetic-programming")
    parser.add_argument("--device", "-d", type=str, default="cpu",
                        help="specifies the device to run the computations on (cpu, cuda, mps)")
    parser.add_argument("--num_vars", "-n", type=int, default=1,
                        help="number of variables/terminals")
    parser.add_argument("--pop_size", "-p", type=int, default=1000, help="population size")
    parser.add_argument("--selection_size", "-s", type=int, default=20, help="selection size")
    parser.add_argument("--init_depth", "-i", type=int, default=6, help="initial depth of the tree")
    parser.add_argument("--max_depth", "-m", type=int, default=20, help="maximum depth of the tree")
    parser.add_argument("--train_iterations", "-t", type=int, default=30000,
                        help="number of training iterations")
    args = parser.parse_args()
    main(**vars(args))
