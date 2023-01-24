import random
import multiprocessing
import numpy as np
from deap import algorithms, base, creator, tools


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
            #    tools.mutUniformInt,
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

        # initialise the population.
        population = self.toolbox.population(n=kwargs.pop("n", 100))

        # run the GA.
        algorithms.eaSimple(
            population,
            self.toolbox,
            cxpb=kwargs.pop("cxpb", 0.5),
            mutpb=kwargs.pop("mutpb", 0.2),
            ngen=kwargs.pop("ngen", 100),
            verbose=False,
        )

        # return the top chromosomes.
        return tools.selBest(population, k=kwargs.pop("k", 1))


def combined_mutation(individual, low, up, indpb):
    """Mutate an individual by replacing attributes, with probability *indpb*,
    by a integer uniformly drawn between *low* and *up* inclusively.
    :param individual: :term:`Sequence <sequence>` individual to be mutated.
    :param low: The lower bound or a :term:`python:sequence` of
                of lower bounds of the range from which to draw the new
                integer.
    :param up: The upper bound or a :term:`python:sequence` of
               of upper bounds of the range from which to draw the new
               integer.
    :param indpb: Independent probability for each attribute to be mutated.
    :returns: A tuple of one individual.
    """

    a = np.random.choice(np.arange(0, 2), p=[0.9, 0.1])
    if a == 0:
        individual = tools.mutUniformInt(individual, low, up, indpb)
    else:
        individual = tools.mutUniformInt(individual, low, up, 1)

    return individual
