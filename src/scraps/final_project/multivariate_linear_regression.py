import numpy as np
import pandas as pd
from scipy.stats import t


class MultivariateLinearRegression:
    def fit(self, y, X):
        """
        Ordinary Least Squares estimator of linear regression weights.
        y = Xb + error

        Parameters
        ----------
        y : numpy matrix or vector, pandas series
            Matrix or vector for dependent variable.
        X : numpy matrix
            Matrix of independent variables.

        Returns
        -------
        self : object
            Fitted Estimator.
        """
        # Convert to numpy dtype
        index = None
        if isinstance(y, (pd.DataFrame, pd.Series)):
            index = y.index
            y = y.to_numpy()
        if isinstance(X, (pd.DataFrame, pd.Series)):
            X = X.to_numpy()

        self.y = y
        self.X = X

        single_regressor: bool = X.ndim == 1

        # Compute weights estimator
        XT_X = X.T @ X
        if single_regressor:
            self.XT_X_inv = 1/XT_X
        else:
            # Create identity matrix
            identity_matrix = np.eye(XT_X.shape[0])

            # Efficient implementation rather than directly finding inverse
            self.XT_X_inv = np.linalg.solve(XT_X, identity_matrix)

        b = np.dot(self.XT_X_inv, X.T @ y)

        # Assign attributes so they can be accessed by the class instance
        self.coefficients = b if isinstance(b, np.ndarray) else [b]
        self.residuals = y - np.dot(X, b)
        self.n_regressand = (self.coefficients.shape[1] if
                             self.coefficients.ndim > 1 else 1)
        self.n_regressor = self.coefficients.shape[0]

        # Reassign index if applicable
        if index is not None:
            self.residuals = pd.Series(self.residuals)
            self.residuals.index = index

        return self

    def summary(
            self, regressands: list[str] = None, regressors: list[str] = None):
        """
        Calculate summary statistics from OLS linear regression.

        Parameters
        ----------
        regressands: list[str], default = None
            Optional parameter for regressand labels.
            Must be a list equal to number of regressands.
        regressors: list[str], default = None
            Optional parameter for regressor labels.
            Must be a list equal to number of regressors.

        Returns
        -------
        summary_stats: pd.DataFrame
            Summary statistics.
        """
        # Get number of observations (number of rows)
        n_obs = self.y.shape[0]

        # Calculations required in output summary
        residual_cov_matrix = np.dot(self.residuals.T, self.residuals) / n_obs
        cov_matrix_regression_coeffs = np.kron(
            residual_cov_matrix, self.XT_X_inv)
        diag_cov_matrix = np.diag(cov_matrix_regression_coeffs) if \
            self.n_regressor > 1 else cov_matrix_regression_coeffs
        standard_error = n_obs / (n_obs - self.n_regressor) * diag_cov_matrix
        standard_error = np.sqrt(standard_error)

        # Use ravel(order="F") method to stack the second column under the
        # first column if coefficient matrix (i.e. more than 1 regressand)
        t_test = self.coefficients.ravel(order="F") / standard_error

        # Calculate p-values
        df = n_obs - self.n_regressor  # degrees of freedom for t distribution
        vfunc = np.vectorize(lambda x: self.calculate_p_value(x, df))
        p_values = vfunc(t_test)

        summary_stats = pd.DataFrame({
            "Coefficient": self.coefficients.ravel(order="F"),
            "Standard Error": standard_error,
            "t-statistic": t_test,
            "p-value (t-dist)": p_values})

        if regressors:
            # Error handling
            if len(regressors) != self.n_regressor:
                raise ValueError(
                    f"Expected list of length {self.n_regressor} "
                    "for regressors")
            else:
                # Create regressor tags for summary dataframe and reorder
                regressor_tags = [x for _ in range(self.n_regressand) for
                                  x in regressors]
                summary_stats.insert(0, "Regressor", regressor_tags)
        if regressands:
            if (len(regressands) != self.n_regressand):
                raise ValueError(f"Expected list of length {self.n_regressand}"
                                 f" for regressands")
            else:
                # Create regressand tags for summary dataframe and reorder
                regressand_tags = [x for x in regressands for _
                                   in range(self.n_regressor)]
                summary_stats.insert(0, "Regressand", regressand_tags)

        return summary_stats

    def add_constant(
            self, x: pd.DataFrame | pd.Series | np.ndarray, prepend=True):
        """
        Add a column of ones

        Parameters
        ----------
        x : numpy ndarray, pd.DataFrame or pd.Series
            N-dimensional array to add ones to.
        prepend : bool
            Prepend constant ones column. If False then ones are appended.

        Returns
        -------
        np.ndarray
            Input object with a column of ones
        """
        # Convert to numpy object
        if isinstance(x, (pd.DataFrame, pd.Series)):
            x = x.to_numpy()

        # Constant addition
        x = [np.ones(x.shape[0]), x]
        x = x if prepend else x[::-1]

        return np.column_stack(x)

    def calculate_p_value(self, t_stat, df, two_tailed=True):
        """
        Calculate p-value from a t-statistic assuming t-distribution.

        Parameters
        ----------
        t_stat: float
            The t-statistic value.
        df: int
            Degrees of freedom.
        two_tailed: bool
            By default compute a two-tailed test.
        """
        # t-distribution cumulative distribution function
        cdf = t.cdf(abs(t_stat), df)

        # Two-tailed p-value
        if two_tailed:
            p_value = 2 * (1 - cdf)
        else:  # One-tailed p-value
            p_value = 1 - cdf

        return p_value
