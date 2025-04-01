import logging

import numpy as np
import statsmodels.api as sm
from statsmodels.regression.rolling import RollingOLS

from .cadf import CADF, CADF_Results

logger = logging.getLogger("stat_arb")


class StatisticalTests:
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

        self.resids = ols.resids
        self.params = ols.params

    def get_residuals(self):
        if not self.resids:
            self.regress_timeseries_with_lookahead_bias()

        return self.resids

    def is_coint_residual_stationary(self, k_vars: int):
        """
        Cointegrated Engler Granger test to verify stationarity of (cointegrated) timeseries

        k_vars: int
            - Number of I(1) series used to form the (cointegrated) timeseries
        """

        cadf: CADF_Results = CADF.test_stationarity(self.get_residuals())
