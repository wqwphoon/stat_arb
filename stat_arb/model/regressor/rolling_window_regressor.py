import logging
from dataclasses import dataclass

import statsmodels.api as sm
from statsmodels.regression.rolling import RollingOLS

from stat_arb.model.regressor import Regressor

logger = logging.getLogger(__name__)


@dataclass
class RollingWindowRegressorInputs:
    window_length: int
    with_constant: bool


class RollingWindowRegressor(Regressor):
    def __init__(self, dependent_variable, independent_variable):
        self.b = dependent_variable
        self.A = independent_variable

    def get_residual(self, inputs: RollingWindowRegressorInputs):
        logger.info("Running rolling regression of timeseries...")
        if inputs.with_constant:
            self.A = sm.add_constant(self.A)  # make a copy?

        ols = RollingOLS(self.b, self.A, window=inputs.window_length, expanding=False).fit()

        return ols
