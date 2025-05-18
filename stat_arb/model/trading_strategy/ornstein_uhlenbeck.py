from typing import Union

import numpy as np
import pandas as pd
from statsmodels.tsa.ar_model import AutoReg, AutoRegResultsWrapper


class OrnsteinUhlenbeckSDE_Results:
    def __init__(self, mu, sigma, half_life):
        """Immutable"""
        self.__mu = mu
        self.__sigma = sigma
        self.__half_life_working_days = half_life

    def get_mu(self) -> float:
        return self.__mu

    def get_sigma(self) -> float:
        return self.__sigma

    def get_half_life_in_working_days(self) -> float:
        return self.__half_life_working_days


class OrnsteinUhlenbeckSDE:
    def __init__(self, x: Union[np.ndarray, pd.Series]):
        self.x = x

    def fit_to_sde(self) -> OrnsteinUhlenbeckSDE_Results:
        """
        Fit stationary process to Ornstein-Uhlenbeck SDE.

        Referece: Statistical Arbitrage in the U.S. Equities Market, Marco Avellaneda and Jeong-Hyun Lee
        """
        ar: AutoRegResultsWrapper = self._fit_autoregressive_model()

        param_dict = dict(zip(ar.model.exog_names, ar.params))

        a = param_dict["const"]
        b = param_dict["y.L1"]
        ar_resid_var = ar.resid.var()

        tau = 1 / 252  # 252 for daily returns (effectively a HARDCODE)

        mu_e = a / (1 - b)  # equilibrium level of residual
        k = -np.log(b) / tau  # speed of mean reversion
        half_life_working_days = np.log(2) / k / tau
        sigma = np.sqrt((ar_resid_var * 2 * k) / (1 - b**2))
        sigma_eq = sigma / np.sqrt(2 * k)

        return OrnsteinUhlenbeckSDE_Results(mu_e, sigma_eq, half_life_working_days)

    def _fit_autoregressive_model(self) -> AutoRegResultsWrapper:
        ar = AutoReg(self.x, lags=1, trend="c")
        return ar.fit()


if __name__ == "__main__":
    x = np.random.normal(size=[100])

    ou = OrnsteinUhlenbeckSDE(pd.Series(x))
    ou.fit_to_sde()

    pass
