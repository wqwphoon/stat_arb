import logging
from typing import Union

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.regression.rolling import RollingOLS

logger = logging.getLogger(__name__)


# TODO: Add Kalman filter and make an ABC for regressor type?
class Regressor:
    def get_residuals(
        self,
        b: Union[np.ndarray, pd.Series, pd.DataFrame],
        A: Union[np.ndarray, pd.Series, pd.DataFrame],
        with_constant: bool = True,
    ) -> pd.Series:

        if not hasattr(self, "resids"):
            self.regress_timeseries_with_lookahead_bias(b, A, with_constant)

        assert self.resids is not None  # for mypy

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
        self,
        b: Union[np.ndarray, pd.Series, pd.DataFrame],
        A: Union[np.ndarray, pd.Series, pd.DataFrame],
        with_constant: bool = True,
    ) -> None:
        logger.info("Running naive regression of timeseries...")
        if with_constant:
            A = sm.add_constant(A)  # make a copy?

        ols = sm.OLS(b, A).fit()

        self.resids: pd.Series = ols.resid
        self.params: pd.Series = ols.params

    def get_beta(self) -> pd.Series:
        param_header = [x for x in self.params.index if x != "const"][0]

        n = len(self.resids)
        beta_scalar = self.params[param_header]
        beta_series = pd.Series(np.ones(shape=(n)) * beta_scalar)
        beta_series.index = self.resids.index

        return beta_series
