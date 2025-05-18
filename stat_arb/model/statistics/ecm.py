from typing import Union

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.regression.linear_model import RegressionResultsWrapper

RESIDUAL_STR = "(Lag 1, Residuals)"


class ErrorCorrectionModel_Results:
    def __init__(self, ols_results: RegressionResultsWrapper):
        self._ols = ols_results

    def is_long_run_mean_reverting(self, alpha: float = 0.05) -> bool:
        """
        Check the Error Correction Model for a statistically significant long run equilibrium.

        Parameters
        ----------
        alpha : float, optional
            - Default is 0.05.
            - Significance level to test statistical significance of regressed residuals term.
        """
        return bool(self._ols.pvalues[RESIDUAL_STR] < alpha)

    def get_long_run_reversion_speed(self) -> float:
        return self._ols.params[RESIDUAL_STR]


class ErrorCorrectionModel:
    @staticmethod
    def fit(
        price_x: pd.Series,
        price_y: pd.Series,
        residual: Union[pd.Series, np.ndarray],
        reverse_regression: bool = False,
    ) -> ErrorCorrectionModel_Results:
        """
        Fit the Error Correction Model.

        Parameters
        ----------
        price_x : pd.Series
            - Price timeseries of security X.
        price_y : pd.Series
            - Price timeseries of security Y.
        residual : pd.Series
            - Timeseries of residual from regressing X onto Y i.e. X = aY + residual
        reverse_regression : bool
            - Regress security Y on security X i.e. plugging in the "wrong way" residuals.
        """
        ticker_x: str = getattr(price_x, "name", "X")
        ticker_y: str = getattr(price_y, "name", "Y")

        # Concatenate series then difference / lag as required
        rhs = pd.concat([price_x, price_y, pd.Series(residual)], axis=1)
        rhs.columns = pd.Index([ticker_x, ticker_y, "Residuals"])

        rhs[f"Δ{ticker_x}"] = rhs[ticker_x].diff()
        rhs[f"Δ{ticker_y}"] = rhs[ticker_y].diff()
        rhs[RESIDUAL_STR] = rhs["Residuals"].shift(1)

        rhs.dropna(inplace=True)

        # Construct LHS (dependent) and RHS (independent) for regression
        if not reverse_regression:
            lhs = rhs[f"Δ{ticker_x}"]
            rhs.drop(columns=[ticker_x, ticker_y, "Residuals", f"Δ{ticker_x}"], inplace=True)
        else:  # reverse regression is True
            lhs = rhs[f"Δ{ticker_y}"]
            rhs.drop(columns=[ticker_x, ticker_y, "Residuals", f"Δ{ticker_y}"], inplace=True)

        # Regress
        ols = sm.OLS(lhs, rhs).fit()

        return ErrorCorrectionModel_Results(ols)
