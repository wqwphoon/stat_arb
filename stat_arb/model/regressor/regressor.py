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
        param_headers = [x for x in self.params.columns if x != "const"]

        beta_series = self.params[param_headers]

        return beta_series
