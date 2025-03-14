import pandas as pd
import numpy as np

from multivariate_linear_regression import MultivariateLinearRegression
from utils import Utils


class VectorAutoRegressiveModel:
    def fit(
            self, x: pd.Series | np.ndarray | pd.DataFrame,
            lags: int = 1):
        """
        Fit an VAR(p) model where p determines the amount of lags.

        Parameters
        ----------
        x: pd.Series, np.ndarray, pd.DataFrame
            Series to fit the AR model on.
        lags: int
            Number of lags

        Returns
        -------
        self: obj
            VectorAutoRegressiveModel class object returned.
        """
        # Create lagged matrix
        lagged_df = self.create_lagged_matrix(x, lags).dropna()

        # Construct X and Y matrices
        X = lagged_df.to_numpy()
        X = np.hstack([np.ones((X.shape[0], 1)), X])  # Add constant
        Y = x.iloc[lags:].to_numpy()  # remove first p entries due to lag

        self.regressors = lagged_df.columns.insert(0, "Constant").to_list()
        self.regressands = Utils.get_name_or_columns(x)

        # Fit the regression
        OLS = MultivariateLinearRegression()
        OLS.fit(Y, X)

        # Unpack regressed results into attributes
        self.OLS = OLS
        self.coefficients = OLS.coefficients
        self.residuals = OLS.residuals

        return self

    def summary(self) -> pd.DataFrame:
        """
        Generate summary statistics for VAR fitting.

        Returns
        -------
        pd.DataFrame
            VAR fitting summary
        """
        return self.OLS.summary(regressands=self.regressands,
                                regressors=self.regressors)

    def create_lagged_matrix(
            self, df: pd.DataFrame, lags: int) -> pd.DataFrame:
        """
        Create lagged matrix given set number of lags.

        Parameters
        ----------
        df: pd.DataFrame
            Matrix to lag
        lags: int
            Number of lags

        Returns
        -------
        lagged_df: pd.DataFrame
            Lagged matrix including NA rows
        """
        # Lagged data
        lagged_data = {}
        for lag in range(1, lags + 1):
            lagged_data[f'Lag {lag}'] = df.shift(lag)

        # Merge lagged data
        lagged_df = pd.concat(lagged_data, axis=1)

        # Format lagged matrix
        if isinstance(lagged_df.columns, pd.MultiIndex):
            headers = lagged_df.columns.map(', '.join).str.strip(',')
            headers = [f"({x})" for x in headers]
        else:
            timeseries_name = Utils.get_name_or_columns(df)[0]
            headers = lagged_df.columns.to_list()
            headers = [f"({x}, {timeseries_name})" for x in headers]
        lagged_df.columns = headers

        return lagged_df

    def get_optimal_lag(
            self, x: pd.Series | np.ndarray | pd.DataFrame,
            max_lags: int = 1):
        """
        Calculate AIC and BIC values.

        Parameters
        ----------
        x: pd.Series | np.ndarray | pd.DataFrame
            Data to fit VAR to
        max_lags: int, default=1
            Maximum number of lags to test

        Returns
        -------
        df: pd.DataFrame
            DataFrame containing lags and Criterion values
        """
        n_obs = x.shape[0]

        # Initialise dictionaries in preparation for DataFrame
        lag_list = [x for x in range(1, max_lags + 1)]
        AIC = []
        BIC = []

        # Iterate through each lag
        for p in lag_list:
            # Fit VAR model
            self.fit(x, lags=p)

            # Calculate components for Criterion
            residuals = self.residuals
            sigma = np.mean(residuals ** 2)
            n_params = len(self.regressors) * len(self.regressands)

            AIC.append(n_obs * np.log(sigma) + 2 * n_params)
            BIC.append(n_obs * np.log(sigma) + n_params * np.log(n_obs))

        # Create Criterion DataFrame
        df = pd.DataFrame({"AIC": AIC, "BIC": BIC}, index=lag_list)

        # Create and append optimal lag row
        optimal_lag = {"AIC": df["AIC"].idxmin(), "BIC": df["BIC"].idxmin()}
        df.loc["Optimal Lag"] = optimal_lag

        return df
