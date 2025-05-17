import logging

import numpy as np
import statsmodels.api as sm
from statsmodels.regression.rolling import RollingOLS

logger = logging.getLogger(__name__)


# TODO: Add Kalman filter and make an ABC for regressor type?
class Regressor:
    def __init__(self):
        self.resids = None

    def get_residuals(self, b: np.ndarray, A: np.ndarray, with_constant: bool = True) -> np.ndarray:
        if not self.resids:
            self.regress_timeseries_with_lookahead_bias(b, A, with_constant)

        return self.resids

    def regress_timeseries_rolling(
        self, b: np.ndarray, A: np.ndarray, with_constant: bool = True, window: int = 252
    ):
        logger.info("Running rolling regression of timeseries...")
        if with_constant:
            A = sm.add_constant(A)  # make a copy?

        ols = RollingOLS(b, A, window=window, expanding=False).fit()

        return ols

    def regress_timeseries_with_lookahead_bias(
        self, b: np.ndarray, A: np.ndarray, with_constant: bool = True
    ):
        logger.info("Running naive regression of timeseries...")
        if with_constant:
            A = sm.add_constant(A)  # make a copy?

        ols = sm.OLS(b, A).fit()

        self.resids = ols.resid
        self.params = ols.params
