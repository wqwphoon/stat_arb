import logging
from abc import ABC, abstractmethod

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


# TODO: Add Kalman filter and make an ABC for regressor type?
class Regressor(ABC):

    @abstractmethod
    def get_residual(self):
        pass

    # @abstractmethod
    # def get_beta(self):
    #     pass

    def get_beta(self) -> pd.Series:
        param_header = [x for x in self.params.index if x != "const"][0]

        n = len(self.resids)
        beta_scalar = self.params[param_header]
        beta_series = pd.Series(np.ones(shape=(n)) * beta_scalar)
        beta_series.index = self.resids.index

        return beta_series
