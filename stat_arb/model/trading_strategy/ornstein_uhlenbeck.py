from typing import Sequence

import numpy as np
from statsmodels.tsa.ar_model import AutoReg, AutoRegResultsWrapper


class OrnsteinUhlenbeckSDE_Results:
    def __init__(self, mu, sigma):
        """Immuatable"""
        self.__mu = mu
        self.__sigma = sigma

    def get_mu(self):
        return self.__mu

    def get_sigma(self):
        return self.__sigma


class OrnsteinUhlenbeckSDE:
    def __init__(self, x: Sequence[float]):
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

        tau = 252  # 252 for daily returns (effectively a HARDCODE)

        mu_e = a / (1 - b)
        k = -np.log(b) * tau
        sigma = np.sqrt((ar_resid_var * 2 * k) / (1 - b**2))
        sigma_eq = sigma / np.sqrt(2 * k)

        return OrnsteinUhlenbeckSDE_Results(mu_e, sigma_eq)

    def _fit_autoregressive_model(self) -> AutoRegResultsWrapper:
        ar = AutoReg(self.x, lags=1, trend="c")
        return ar.fit()


if __name__ == "__main__":
    x = np.random.normal(size=[100])

    ou = OrnsteinUhlenbeckSDE(x)
    ou.fit_to_sde()

    pass
