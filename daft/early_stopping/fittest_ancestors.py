# Standard imports
from typing import Any, List

# External imports
import numpy as np
from typeguard import typechecked


@typechecked
class FittestAncestors:
    """
    Saves the best individual of each generation and their fitness value.
    """

    def __init__(self, num_gen: int) -> None:
        """
        Initialise the FittestAncestors class.

        Parameters
        ----------
        num_gen : int
            The current generation.

        """
        self.fittest_ancestors = np.empty(num_gen + 1, dtype=object)
        self.fits = np.zeros(num_gen + 1, dtype=float)
        self.gen = 0

    def update(self, population: List[Any]) -> None:
        """
        Update the fittest ancestors and their fitness values.

        Parameters
        ----------
        population : list
            The population of individuals.

        """
        fits = [ind.fitness.values[0] for ind in population]
        fittest_ind = np.argmin(fits)
        self.fittest_ancestors[self.gen] = population[fittest_ind]
        self.fits[self.gen] = fits[fittest_ind]
        self.gen += 1
