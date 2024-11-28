# Standard imports
from enum import Enum
from typeguard import typechecked
from abc import ABC, abstractmethod

# Internal imports
from .fittest_ancestors import FittestAncestors


class GAEarlyStopperMethods(Enum):
    PLATEAU = "plateau"


@typechecked
class EarlyStopper(ABC):
    @abstractmethod
    def stop_early(self, fittest_ancestors: FittestAncestors) -> bool:
        pass
