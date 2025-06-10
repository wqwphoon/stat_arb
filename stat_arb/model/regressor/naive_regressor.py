import logging
from dataclasses import dataclass
from typing import Union

import numpy as np
import pandas as pd
import statsmodels.api as sm

from stat_arb.model.regressor.regressor import Regressor

logger = logging.getLogger(__name__)


@dataclass
class NaiveRegressorInputs:
    pass


# Naive regression of timeseries with lookahead bias
class NaiveRegressor(Regressor):
    def __init__(
        self,
        dependent_variable: Union[np.ndarray, pd.Series, pd.DataFrame],
        independent_variable: Union[np.ndarray, pd.Series, pd.DataFrame],
    ):
        self.b = dependent_variable
        self.A = independent_variable

    def get_residual(self, inputs: NaiveRegressorInputs):
        logger.info("Running naive regression of timeseries...")

        # if inputs.with_constant:
        self.A = sm.add_constant(self.A)

        ols = sm.OLS(self.b, self.A).fit()

        self.params = ols.params
        self.resids = ols.resid

        return self.resids
