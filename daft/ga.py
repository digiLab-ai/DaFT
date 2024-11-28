import json
import random
import multiprocessing
import numpy as np
from tqdm import tqdm
from typing import Any
from deap import algorithms, base, creator, tools

from .early_stopping.fittest_ancestors import FittestAncestors
from .early_stopping.early_stoppers.plateau import Plateau


class IndexSelectionGA:
    """
    IndexSelectionGA is a class that sets up a Genetic Algorithm that will
    minimise a fitness function over a list of indices.

    Attributes
    ----------
    n_sub : int
        How many indices to return.
    n_total : int
        How many total indices.
    fitness_min : callable
        The fitness function to minimise.
    toolbox : deap.base.Toolbox
        A DEAP Toolbox instance.
    indpb_mate : float
        The probability of swapping genes when mating two chromosomes.
    indpb_mutate : float
        The probability of mutating each gene during mutation.
    tournsize : int
        The tournament size for chromosome selection.

    Methods
    ----------
    run(**kwargs)
        Run the Genetic Algorithm.
    """

    def __init__(self, n_sub, n_total, fitness_min, **kwargs):
        """
        Parameters
        ----------
        n_sub : int
            How many indices to return.
        n_total : int
            How many total indices.
        fitness_min : callable
            The fitness function to minimise.
        multiprocessing : bool, optional.
            Whether to use multiprocessing, default is True.
        indpb_mate : float, optional
            The probability of swapping genes when mating two chromosomes.
            Default is 0.2
        indpb_mutate : float, optional
            The probability of mutating each gene during mutation. Default
            is 0.1
        tournsize : int, optional
            The tournament size for chromosome selection. Default is 3.

        Returns
        ----------
        None
        """

        # set the number of indices to return and the total number of indices.
        self.n_sub = n_sub
        self.n_total = n_total

        # set the fitness function to be minimised.
        self.fitness_min = fitness_min

        # initialise the fitness function with DEAP.
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))

        # initialise the individial (chromosome) with DEAP.
        creator.create("Individual", list, fitness=creator.FitnessMin)

        # initialise a DEAP Toolbox.
        self.toolbox = base.Toolbox()

        # set up multiprocessing, if requested.
        if kwargs.pop("multiprocessing", True):
            self.toolbox.register("map", multiprocessing.Pool().map)

        # define the parameter space as a random sample from the indices.
        self.toolbox.register("indices", random.sample, range(self.n_total), self.n_sub)

        # initilise the individuals, population and the evaluation function.
        self.toolbox.register(
            "individual", tools.initIterate, creator.Individual, self.toolbox.indices
        )
        self.toolbox.register(
            "population", tools.initRepeat, list, self.toolbox.individual
        )
        self.toolbox.register("evaluate", self.fitness_min)

        # set up random uniform mating.
        self.indpb_mate = kwargs.pop("indpb_mate", 0.2)
        self.toolbox.register("mate", tools.cxUniform, indpb=self.indpb_mate)

        # set up mutation to be random uniform dram from indices.
        self.indpb_mutate = kwargs.pop("indpb_mutate", 0.1)
        self.toolbox.register(
            "mutate",
            combined_mutation,
            low=0,
            up=self.n_total - 1,
            indpb=self.indpb_mutate,
        )

        # set up the tournament selection process.
        self.tournsize = kwargs.pop("tournsize", 3)
        self.toolbox.register("select", tools.selTournament, tournsize=self.tournsize)

    def run(self, **kwargs):
        """
        Run the Genetic Algorithm.

        Parameters
        ----------
        n : int, optional.
            How large a population to use. Default is 100.
        ngen : int, optional
            How many generations to run the GA. Default is 100.
        k : int, optional
            How many chromosomes to return. Default is 1.
        cxpb : float, optional
            The probability of mating. Default is 0.5.
        mutpb : float, optional
            The probability of mutating. Default is 0.2.

        Returns
        ----------
        list
        """
        ngen = kwargs.pop("ngen", 100)  # The number of generations
        cxpb = kwargs.pop("cxpb", 0.5)  # The probability of mating
        mutpb = kwargs.pop("mutpb", 0.2)  # The probability of mutating
        checkpoint = kwargs.pop("checkpoint", False)  # Whether to checkpoint
        checkpoint_dir = kwargs.pop("checkpoint_dir", "results")

        # setup checkopointing to pickup where we left off
        if kwargs.pop("checkpoint", None) is None:
            start_gen = 0
            population = self.toolbox.population(
                n=kwargs.pop("n", 100)
            )  # Initialise the population
        else:
            start_gen, population = self._load_from_json(
                kwargs.pop("checkpoint_path", None)
            )

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in population if not ind.fitness.valid]
        fitnesses = self.toolbox.map(self.toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # Initialise the fittest ancestor storage
        fittest_ancestors = FittestAncestors(num_gen=ngen)
        fittest_ancestors.update(population)

        early_stopper = kwargs.pop("early_stopper", Plateau)(**kwargs)

        for gen in tqdm(range(start_gen, ngen), desc="GA Generation"):
            # select the next generation individuals
            offspring = self.toolbox.select(population, len(population))

            # vary the pool of individuals
            offspring = self._varAnd(offspring, cxpb, mutpb)

            # evaluate the individuals with an invalid fitness
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = self.toolbox.map(self.toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            # replace the current population by the offspring
            population[:] = offspring

            # update the fittest ancestors
            fittest_ancestors.update(population)

            best_individual = tools.selBest(population, k=1)[0]

            if checkpoint:
                self._save_to_json(population, best_individual, checkpoint_dir, gen)

            # check for early stopping
            if early_stopper.stop_early(fittest_ancestors):
                print(f"Stopped early at generation {gen}")
                break

        # return the top chromosomes.
        return tools.selBest(population, k=kwargs.pop("k", 1))

    def _varAnd(self, population: list, prob_mate: float, prob_mutate: float) -> list:
        """
        Vary the population by mating and mutating the offspring.

        Parameters
        ----------
        population : list
            The population of individuals.
        prob_mate : float
            The probability of mating.
        prob_mutate : float
            The probability of mutating.

        Returns
        -------
        offspring : list
            The offspring (which go on to replace the population).
        """

        offspring = [self.toolbox.clone(ind) for ind in population]

        # Mating and mutating of the offspring
        for i in range(1, len(offspring), 2):
            # Mating
            if random.random() < prob_mate:
                offspring[i - 1], offspring[i] = self.toolbox.mate(
                    offspring[i - 1], offspring[i]
                )
                del offspring[i - 1].fitness.values, offspring[i].fitness.values
        # Mutating
        for i in range(len(offspring)):
            if random.random() < prob_mutate:
                (offspring[i],) = self.toolbox.mutate(offspring[i])
                del offspring[i].fitness.values

        return offspring

    def _save_to_json(
        self, population: list, best_individual: object, dir_name: str, gen: int
    ) -> None:
        """
        Save the genetic algorithm state to a JSON file.

        Parameters
        ----------
        data : Dict[str, Any]
            The data to be saved to the JSON file.
        dir_name : str
          Name of folder to save JSON files in.
        gen : int
            The generation number.
        """

        data = {
            "generation": gen,
            "population": [list(ind) for ind in population],
            "best_individual": list(best_individual),
            "best_fitness": best_individual.fitness.values[0],
        }

        file_name = f"{dir_name}/generation_{gen}.json"
        with open(file_name, "w") as f:
            json.dump(data, f, indent=4)

    def _load_from_json(self, file_path: str) -> dict[str, Any]:
        """
        Load the genetic algorithm state from a JSON file.

        Parameters
        ----------
        file_path : str
            Path to the JSON file

        Returns
        -------
        data : Dict[str, Any]
            The data from the JSON file.
        """
        with open(file_path, "r") as f:
            data = json.load(f)
        start_gen = data["generation"] + 1
        population = [creator.Individual(ind) for ind in data["population"]]
        return start_gen, population


def combined_mutation(individual, low, up, indpb):
    """
    Firstly the type of mutation is choosed with 90% and 10% accordigly.
    The first mutation type mutates an individual by replacing attributes,
    with probability *indpb*, by a integer uniformly drawn between *low*
    and *up* inclusively.The second mutation type mutates a whole individual
    by replacing all attibuttes by ingegeres uniformly drawn by the initial chain.

    Parameters
    ----------
    individual : np.ndarray
        individual to be mutated.
    low : int
        The lower bounds of the range from which to draw the new
        integer.
    up : int
        The upper bound of the range from which to draw the new
        integer.
    indpb : int
        Independent probability for each attribute to be mutated.

    Returns
    ----------
    tuple
    """

    # normal mutation with chance of 90%
    if np.random.uniform() < 0.9:
        individual = tools.mutUniformInt(individual, low, up, indpb)
    # completly new chromosome with chance 10%
    else:
        individual = tools.mutUniformInt(individual, low, up, 1)

    return individual
