from statsmodels.tsa.adfvalues import mackinnoncrit, mackinnonp
from statsmodels.tsa.stattools import adfuller


class CADF_Results:
    def __init__(self, test_statistic: float, p_value: float, criticial_values: list[float]):
        self.t_stat = test_statistic
        self.p_val = p_value
        self.c_vals = criticial_values

    def get_test_statistic(self) -> float:
        return self.t_stat

    def get_p_value(self) -> float:
        return self.p_val

    def get_critical_values(self) -> list[float]:
        return self.c_vals

    def significant_at_one_pct(self) -> bool:
        return (self.p_val < 0.01).item()

    def significant_at_five_pct(self) -> bool:
        return (self.p_val < 0.05).item()

    def significant_at_ten_pct(self) -> bool:
        return (self.p_val < 0.1).item()

    def summary(self) -> dict[str, float | list[float]]:
        return {
            "test_statistic": self.get_test_statistic(),
            "p-value": self.get_p_value(),
            "critical_values": self.get_critical_values(),
        }


class CADF:
    @staticmethod
    def test_stationarity(x, k_vars=1) -> CADF_Results:
        """
        Cointegrated Augmented Dickey Fuller stationarity test.

        Parameters
        ----------
        x : array-like
            - Timeseries to test for stationarity.
        k_var : int, optional
            - Number of I(1) timeseries used to construct the cointegrated residual x.
        """
        n_obs = x.shape[0]

        t_stat: float = adfuller(x)[0]

        c_vals: list[float] = mackinnoncrit(N=k_vars, nobs=n_obs - 1)

        # TODO: flexibility to relax regression="c" HARDCODE
        p_val: float = mackinnonp(teststat=t_stat, regression="c", N=k_vars)

        return CADF_Results(t_stat, p_val, c_vals)
