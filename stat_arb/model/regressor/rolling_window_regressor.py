import logging
from dataclasses import dataclass

import numpy as np
import statsmodels.api as sm
from statsmodels.regression.rolling import RollingOLS

from stat_arb.model.regressor import Regressor

logger = logging.getLogger(__name__)


@dataclass
class RollingWindowRegressorInputs:
    window_length: int


class RollingWindowRegressor(Regressor):
    def __init__(self, dependent_variable, independent_variable):
        self.b = dependent_variable
        self.A = independent_variable

    def get_residual(self, inputs: RollingWindowRegressorInputs):
        logger.info("Running rolling regression of timeseries...")

        # if inputs.with_constant:
        self.A = sm.add_constant(self.A)  # make a copy?

        ols = RollingOLS(self.b, self.A, window=inputs.window_length, expanding=False).fit()

        self.params = ols.params

        df = self.params.copy()
        df.columns = [f"{x}_params" for x in df.columns]
        df[self.A.columns] = self.A

        n = df.shape[1] // 2  # find column-wise midpoint of dataframe
        result = df.iloc[:, :n].values * df.iloc[:, n:].values
        regressed_columns = [f"{x}_regressed" for x in self.A.columns]
        df[regressed_columns] = result

        df["Fitted_Values"] = df[regressed_columns].sum(axis=1)
        df.loc[df[regressed_columns[0]].isna(), "Fitted_Values"] = np.nan  # lost data due to rolling window
        df.loc[: df.index[inputs.window_length - 1], "Fitted_Values"] = np.nan
        df[self.b.name] = self.b
        df["Residuals"] = df[self.b.name] - df["Fitted_Values"]

        self.resids = df["Residuals"]

        return self.resids
