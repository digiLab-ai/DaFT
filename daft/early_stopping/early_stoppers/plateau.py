# Standard imports
from typing import Optional
from typeguard import typechecked

# Local imports
from ..fittest_ancestors import FittestAncestors
from ..early_stopper import EarlyStopper


class Plateau(EarlyStopper):
    """
    A class to stop the genetic algorithm early if the fitness has plateaued.
    """

    def __init__(self, **kwargs) -> None:
        """
        Initialise the Plateau early stopper.

        Parameters
        ----------
        threshold : float, optional
            The threshold for the fitness to plateau, by default 0.001
        window_size : int, optional
            The window size to check for the plateau, by default 20
        """
        self.threshold = kwargs.pop("threshold", 0.001)
        self.window_size = kwargs.pop("window_size", 20)

    def stop_early(self, fittest_ancestors: FittestAncestors):
        """
        Check if the fitness has plateaued.

        Parameters
        ----------
        fittest_ancestors : FittestAncestors
            The fittest ancestors object.
        """
        gen = fittest_ancestors.gen

        if gen < self.window_size:
            return False

        window = fittest_ancestors.fits[gen - self.window_size : gen]

        return max(window) - min(window) < self.threshold
