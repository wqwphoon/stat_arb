import numpy as np
import pandas as pd

from multivariate_linear_regression import MultivariateLinearRegression
from utils import Utils


class ADF:
    def stationarity_test(
            self, x: np.ndarray | pd.Series,
            coint_n_timeseries: int, include_constant=True):
        """
        Perform the Augmented Dickey-Fuller test.

        The trend term is excluded.

        Parameters
        ----------
        x: pd.Series, np.ndarray
            Timeseries to test for stationarity.
        coint_n_timeseries: int
            Number of I(1) series for which null of non-cointegration tests
            e.g. for bivariate Engle-Granger procedure, coint_n_timeseries=2
        include_constant: bool
            Whether a constant term should be included in the OLS regression
            for ADF stationarity testing.

        Returns
        -------
        pd.DataFrame
            Summary of stationarity tests under 1%, 5%, 10% significance
        -------

        """
        # Convert to pandas dataframe for useful methods such as shift & diff
        rhs = pd.DataFrame(x) if not isinstance(x, pd.DataFrame) else x

        # Ensure only one vector of data
        if len(rhs.columns) != 1:
            raise ValueError(
                "Expected a 1D vector, but received a multidimensional matrix")

        # Name the timeseries
        ts = Utils.get_vector_name(x, default_name="x")
        rhs = rhs.rename(columns={rhs.columns[0]: ts})

        # Assumes one lag
        rhs[f"Δ{ts}"] = rhs[ts].diff()
        rhs[f"(Lag 1, {ts})"] = rhs[ts].shift(1)
        rhs[f"(Lag 1, Δ{ts})"] = rhs[f"Δ{ts}"].shift(1)

        if include_constant:
            rhs["Constant"] = 1

        rhs.dropna(inplace=True)
        n_obs = rhs.shape[0]

        # Construct LHS (dependent) and RHS (independent)
        lhs = rhs[f"Δ{ts}"]
        rhs.drop(columns=[ts, f"Δ{ts}"], inplace=True)

        # Regress using OLS
        OLS = MultivariateLinearRegression()
        OLS.fit(lhs, rhs)

        # Get t-statistic and drop p-value col as it is not based off DF-dist
        OLS_summary = OLS.summary()
        OLS_summary.drop(columns="p-value (t-dist)", inplace=True)
        OLS_summary["Regressor"] = rhs.columns
        OLS_summary.set_index("Regressor", inplace=True)

        self.OLS_summary = OLS_summary

        # Critical values from MacKinnon approx
        c_vals = self.calculate_dickey_fuller_critical_value(
            coint_n_timeseries, include_constant, n_obs)

        # Locate t-statistic for lagged term to test against DF-dist
        t_stat = self.OLS_summary.loc[f"(Lag 1, {ts})"]["t-statistic"]

        # Create summary dataframe
        ADF_summary = {
            "Regressand": f"Δ{ts}",
            "Regressor": f"(Lag 1, {ts})",
            "t-statistic": t_stat,
            "Significance Level": ["1%", "5%", "10%"],
            "Critical Value": c_vals}
        ADF_summary = pd.DataFrame(ADF_summary)
        if not np.isnan(c_vals).all():
            ADF_summary["Is Stationary"] = (ADF_summary["t-statistic"] <
                                            ADF_summary["Critical Value"])
        else:
            ADF_summary["Is Stationary"] = "NA"

        self.ADF_summary = ADF_summary

        return self.ADF_summary

    def calculate_dickey_fuller_critical_value(
            self, coint_n_timeseries: int, include_constant: bool,
            n_obs: int) -> list[float]:
        """
        Test t-statistic against MacKinnon's Dickey-Fuller approximation.
        Get MacKinnon's coefficients for approximation across
        1%, 5%, 10% significance.

        Parameters
        ----------
        coint_n_timeseries: int
            Number of I(1) series for which null of non-cointegration tests
            e.g. for bivariate Engle-Granger procedure, coint_n_timeseries=2
        include_constant: bool
            Boolean for whether a constant was included in the regression
        n_obs: int
            Number of observations

        Returns
        -------
        list[float]
            Dickey-Fuller critical values across 1%, 5%, 10% significance

        """
        # Determine which beta table to point to
        if include_constant:
            beta_coeffs = tau_c_2010[coint_n_timeseries-1]
        elif coint_n_timeseries == 1:  # no constant
            beta_coeffs = tau_nc_2010[0]
        else:
            beta_coeffs = [[np.nan for _ in range(4)] for __ in range(3)]

        # Calculate critical values from MacKinnon's approximation
        critical_vals = []
        for b in beta_coeffs:
            c_val = b[0] + b[1]/n_obs + b[2]/n_obs**2 + b[3]/n_obs**3
            critical_vals.append(c_val)

        return critical_vals


"""
Static tables in Python taken from statsmodels.tsa.adfvalues
"""
# These are the new estimates from MacKinnon 2010
# the first axis is N -1
# the second axis is 1 %, 5 %, 10 %
# the last axis is the coefficients

tau_nc_2010 = [[
    [-2.56574, -2.2358, -3.627, 0],  # N = 1
    [-1.94100, -0.2686, -3.365, 31.223],
    [-1.61682, 0.2656, -2.714, 25.364]]]
tau_nc_2010 = np.asarray(tau_nc_2010)

tau_c_2010 = [
    [[-3.43035, -6.5393, -16.786, -79.433],  # N = 1, 1%
     [-2.86154, -2.8903, -4.234, -40.040],   # 5 %
     [-2.56677, -1.5384, -2.809, 0]],        # 10 %
    [[-3.89644, -10.9519, -33.527, 0],       # N = 2
     [-3.33613, -6.1101, -6.823, 0],
     [-3.04445, -4.2412, -2.720, 0]],
    [[-4.29374, -14.4354, -33.195, 47.433],  # N = 3
     [-3.74066, -8.5632, -10.852, 27.982],
     [-3.45218, -6.2143, -3.718, 0]],
    [[-4.64332, -18.1031, -37.972, 0],       # N = 4
     [-4.09600, -11.2349, -11.175, 0],
     [-3.81020, -8.3931, -4.137, 0]],
    [[-4.95756, -21.8883, -45.142, 0],       # N = 5
     [-4.41519, -14.0405, -12.575, 0],
     [-4.13157, -10.7417, -3.784, 0]],
    [[-5.24568, -25.6688, -57.737, 88.639],  # N = 6
     [-4.70693, -16.9178, -17.492, 60.007],
     [-4.42501, -13.1875, -5.104, 27.877]],
    [[-5.51233, -29.5760, -69.398, 164.295],  # N = 7
     [-4.97684, -19.9021, -22.045, 110.761],
     [-4.69648, -15.7315, -5.104, 27.877]],
    [[-5.76202, -33.5258, -82.189, 256.289],  # N = 8
     [-5.22924, -23.0023, -24.646, 144.479],
     [-4.95007, -18.3959, -7.344, 94.872]],
    [[-5.99742, -37.6572, -87.365, 248.316],  # N = 9
     [-5.46697, -26.2057, -26.627, 176.382],
     [-5.18897, -21.1377, -9.484, 172.704]],
    [[-6.22103, -41.7154, -102.680, 389.33],  # N = 10
     [-5.69244, -29.4521, -30.994, 251.016],
     [-5.41533, -24.0006, -7.514, 163.049]],
    [[-6.43377, -46.0084, -106.809, 352.752],  # N = 11
     [-5.90714, -32.8336, -30.275, 249.994],
     [-5.63086, -26.9693, -4.083, 151.427]],
    [[-6.63790, -50.2095, -124.156, 579.622],  # N = 12
     [-6.11279, -36.2681, -32.505, 314.802],
     [-5.83724, -29.9864, -2.686, 184.116]]]
tau_c_2010 = np.asarray(tau_c_2010)
