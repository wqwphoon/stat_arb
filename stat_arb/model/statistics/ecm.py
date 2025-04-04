from typing import Sequence

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.regression.linear_model import RegressionResultsWrapper


class ECM_Results:
    def __init__(self, ols_results: RegressionResultsWrapper):
        self._ols = ols_results


class ECM:
    @staticmethod
    def check_long_run_equilibrium(
        price_x: Sequence[float],
        price_y: Sequence[float],
        residual: Sequence[float],
        reverse_regression: bool = False,
    ) -> ECM_Results:
        """
        Check the Error Correction Model for a statistically significant long run equilibrium.

        Parameters
        ----------
        price_x : Sequence[float]
            - Price timeseries of security X.
        price_y : Sequence[float]
            - Price timeseries of security Y.
        residual : Sequence[float]
            - Timeseries of residual from regressing X onto Y i.e. X = aY + residual
        reverse_regression : bool
            - Regress security Y on security X i.e. plugging in the "wrong way" residuals.
        """
        ticker_x: str = getattr(price_x, "name", "X")
        ticker_y: str = getattr(price_x, "name", "Y")

        # Concatenate series then difference / lag as required
        rhs = pd.concat([price_x, price_y, residual], axis=1)
        rhs.columns = [ticker_x, ticker_y, "Residuals"]

        rhs[f"Δ{ticker_x}"] = rhs[ticker_x].diff()
        rhs[f"Δ{ticker_y}"] = rhs[ticker_y].diff()
        rhs["(Lag 1, Residuals)"] = rhs["Residuals"].shift(1)

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

        return ECM_Results(ols)


if __name__ == "__main__":
    x = np.random.random_integers(-3, 10, size=(10, 1)).cumsum()
    y = np.random.random_integers(-3, 10, size=(10, 1)).cumsum()
    res = np.random.normal(size=(10, 1))

    ecm = ECM.check_long_run_equilibrium(x, y, res)

    pass
