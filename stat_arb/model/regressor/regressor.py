import logging
from abc import ABC, abstractmethod

import pandas as pd

logger = logging.getLogger(__name__)


# TODO: Add Kalman filter and make an ABC for regressor type?
class Regressor(ABC):

    @abstractmethod
    def get_residual(self, inputs):
        pass

    @abstractmethod
    def get_beta(self) -> pd.Series:
        pass
