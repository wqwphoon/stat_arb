import logging

import numpy as np
import pandas as pd

from .cadf import CADF, CADF_Results

logger = logging.getLogger("stat_arb")


class StatisticalTests:
    def __init__(self, x: np.array | pd.Series | pd.DataFrame, k_vars: int = 1):
        """
        x : array-like
            - Timeseries of residual.
        k_vars : int
            - Number of I(1) series used to form the (cointegrated) timeseries.
        """
        self.x = x
        self.k_vars = k_vars

    def run(self):
        stationary: bool = self.is_coint_residual_stationary(self.x)

    # TODO: possible refactoring to make it return cadf.summary() rather than a sole bool
    def is_coint_residual_stationary(self) -> bool:
        """
        Cointegrated Engler Granger test to verify stationarity of (cointegrated) timeseries.
        """

        cadf: CADF_Results = CADF.test_stationarity(self.x, k_vars=self.k_vars)

        return cadf.significant_at_five_pct()

    def error_correction_model(self) -> bool: ...
