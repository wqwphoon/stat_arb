import warnings
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import matplotlib.dates as mdates
from IPython.display import display
from pyfolio import create_returns_tear_sheet

from multivariate_linear_regression import MultivariateLinearRegression
from augmented_dickey_fuller import ADF
from vector_autoregressive_model import VectorAutoRegressiveModel
from timeseries_data import TimeseriesData

warnings.filterwarnings('ignore')


class BivariateEngleGranger:
    def initialise_single_procedure(
            self, ticker_a: str, ticker_b: str,
            start_date: str, end_date: str, live_start_date: str = None,
            benchmark: str = None):
        """
        Initialise a single procedure for Bivariate Engle Granger.

        Parameters
        ----------
        ticker_a: str
            Yahoo Finance ticker for first security
        ticker_b: str
            Yahoo Finance ticker for second security
        start_date: str
            Date for analysis to begin
            Format YYYY-MM-DD
        end_date: str
            Date for analysis to end
            Format YYYY-MM-DD
        live_start_date: str, default = None
            Date for test period to begin
            Format YYYY-MM-DD
        benchmark: str, default = None
            Yahoo Finance ticker for benchmark
        """
        self.ticker_a: str = ticker_a
        self.ticker_b: str = ticker_b
        self.start_date: str = start_date
        self.end_date: str = end_date
        self.live_start_date: str = live_start_date
        self.benchmark: str = benchmark

    def run_single_procedure(self, include_strategy_backtest: bool = True):
        """
        After initialising, we run a single procedure here.

        Parameters
        ----------
        include_strategy_backtest: bool, default=True
            Generate and display backtest outputs
        """

        self.get_close_prices_timeseries()

        self.normalise_bivariate_timeseries()

        print(f"Price regression summary "
              f"{'(training dataset)' if self.live_start_date else ''}")
        OLS_stats = self.regress_timeseries(include_constant=True)
        display(OLS_stats)

        print("\n\nTimeseries plots")
        self.plot_timeseries()

        print(f"\n\nCointegrated Augmented Dickey-Fuller test "
              f"{'(training dataset)' if self.live_start_date else ''}")
        ADF_stats = self.is_residual_stationary(cadf_include_constant=True)
        display(ADF_stats)

        print(f"\n\nError Correction Model fitting "
              f"{'(training dataset)' if self.live_start_date else ''}")
        ECM_stats = self.check_error_correction_model_mean_reversion()
        display(ECM_stats)

        print(f"\n\nError Correction Model reverse fitting "
              f"{'(training dataset)' if self.live_start_date else ''}")
        ECM_reverse_stats = self.check_error_correction_model_mean_reversion(
            reverse_regression=True)  # secondary check
        display(ECM_reverse_stats)

        print(f"\n\nFit to Ornstein-Uhlenbeck Stochastic Differential Equation"
              f" {'(training dataset)' if self.live_start_date else ''}")
        self.fit_to_ornstein_uhlenbeck_sde()

        print(f"\n\nGrid search optimisation results for Z "
              f"{'(training dataset)' if self.live_start_date else ''}")
        z_table, df_optimal_trades = self.optimise_trading_strategy()
        display(z_table)

        print("\n\nBacktest plots for optimal Z")
        self.plot_backtest(df_optimal_trades, trade_markers=True)

        if include_strategy_backtest:
            print("\n\nRolling beta with respect to S&P500 excess returns")
            self.plot_sp500_xs_rets_rolling_beta(df_optimal_trades)

            print("\n\nTearsheet generation")
            self.create_pyfolio_returns_tear_sheet(df_optimal_trades)

    def run_batch_procedure(
            self, run_locally=True, corr_threshold: float = 0.9):
        """
        Run batch Engle Granger procedure.

        Parameters
        ----------
        run_locally: bool, default=True
            If true, price timeseries are called from sp_500.db.
            If false, S&P500 tickers are scraped and price timeseries are
            taken from yfinance and put into a database.
        corr_threshold: float, default=0.9
            Correlation threshold for filtering ahead of testing for
            stationarity.

        Returns
        -------
        df: pd.DataFrame
            DataFrame containing stationarity test results for batch run
        """
        # Hardcode date range for yfinance pricing timeseries extraction
        start_date_batch = "2010-01-01"
        end_date_batch = "2024-11-29"

        # Assign required attributes
        self.start_date: str = start_date_batch
        self.end_date: str = end_date_batch
        self.benchmark: str = None

        sp500_data = TimeseriesData()

        # Run locally vs call yfinance
        if run_locally:
            sp500_data.run_locally()
        else:
            sp500_data.scrape_sp500_constituents()
            sp500_data.create_sp500_database(
                start=start_date_batch, end=end_date_batch)

        # Dataframe containing Adj Close prices of all S&P 500 constituents
        df = sp500_data.aggregate_adj_close()

        # No train test split for batch procedure
        self.n_in_sample = len(df)
        self.n_out_sample = 0

        # Dataframe containing constituent sectors
        sector_df = sp500_data.get_constituents_sector()

        # Retrieve highly correlated pairs
        pairs = sp500_data.get_correlated_pairs(threshold=corr_threshold)

        # Run beginning portion of EG procedure on each pair
        pair_dfs = []
        for pair in pairs:
            batch_a, batch_b, corr = pair

            print(f"\nProcessing pair {batch_a}-{batch_b}")

            self.ticker_a = batch_a
            self.ticker_b = batch_b
            self.raw_price_a = df[batch_a]
            self.raw_price_b = df[batch_b]

            self.normalise_bivariate_timeseries()

            OLS_stats = self.regress_timeseries(include_constant=True)

            # Run stationarity tests and format output
            try:
                ADF_stats = self.is_residual_stationary(
                    cadf_include_constant=True)
                ADF_stats.insert(0, "Ticker A", self.ticker_a)
                ADF_stats.insert(1, "Ticker B", self.ticker_b)
                ADF_stats.insert(2, "Ticker A Sector",
                                 sector_df.loc[self.ticker_a].Sector)
                ADF_stats.insert(3, "Ticker B Sector",
                                 sector_df.loc[self.ticker_b].Sector)
                ADF_stats.insert(4, "Ticker A Industry",
                                 sector_df.loc[self.ticker_a].Industry)
                ADF_stats.insert(5, "Ticker B Industry",
                                 sector_df.loc[self.ticker_b].Industry)
            except np.linalg.LinAlgError:
                print(f"ADF test for {batch_a}-{batch_b} "
                      f"failed with LinAlgError")

            pair_dfs.append(ADF_stats)

        # Create dataframe with all successful stationarity test results
        df = pd.concat(pair_dfs).reset_index(drop=True)

        return df

    def _get_yf_data(self, ticker_str: str) -> pd.Series:
        """
        Pull pricing data from yfinance.

        Parameters
        ----------
        ticker_str: str
            String of Yahoo Finance ticker

        Returns
        -------
        ticker: pd.Series
            Pricing timeseries for the relevant ticker
        """
        ticker = yf.Ticker(ticker_str)
        ticker = ticker.history(start=self.start_date, end=self.end_date,
                                interval="1d")
        return ticker

    def get_close_prices_timeseries(self):
        """
        Get the close price timeseries for tickers and benchmark.
        """
        # Get pricing data from yfinance
        self.raw_price_a: pd.Series = self._get_yf_data(self.ticker_a).Close
        self.raw_price_b: pd.Series = self._get_yf_data(self.ticker_b).Close

        # Data cleaning to ensure the same date timestamp indices
        combined_index = self.raw_price_a.index.union(self.raw_price_b.index)
        self.raw_price_a = self.raw_price_a.reindex(combined_index).ffill()
        self.raw_price_b = self.raw_price_b.reindex(combined_index).ffill()

        self.raw_price_a.name = self.ticker_a
        self.raw_price_b.name = self.ticker_b

        # Calculate number of observations in training vs test dataset
        if self.live_start_date:
            self.n_in_sample = (combined_index < self.live_start_date).sum()
            self.n_out_sample = (combined_index >= self.live_start_date).sum()
        else:
            self.n_in_sample = len(combined_index)
            self.n_out_sample = 0

        if self.benchmark:
            self.price_benchmark: pd.Series = self._get_yf_data(
                self.benchmark).Close
            self.price_benchmark.name = self.benchmark

    def normalise_timeseries(self, x: pd.Series):
        """
        Normalise timeseries to start at 1.

        Parameters
        ----------
        x: pd.Series
            Timeseries to normalise

        Returns
        -------
        pd.Series
            Normalised timeseries 
        """
        return x / x.iloc[0]

    def normalise_bivariate_timeseries(self):
        """
        Normalise tickers and benchmark for bivariate setup.
        """
        # Normalise timeseries
        self.price_a: pd.Series = self.normalise_timeseries(self.raw_price_a)
        self.price_b: pd.Series = self.normalise_timeseries(self.raw_price_b)

        if self.benchmark:
            self.price_benchmark: pd.Series = self.normalise_timeseries(
                self.price_benchmark)

    def regress_timeseries(self, include_constant: bool = True):
        """
        Regress ticker_a onto ticker_b.

        Parameters
        ----------
        include_constant: bool, default=True
            Include a constant term in the regression

        Returns
        -------
        summary_table: pd.DataFrame
            Summary statistics for the regression
        """
        # Initialise linear regression class        
        OLS = MultivariateLinearRegression()

        # Wrangle training data into correct form
        y = self.price_a.iloc[:self.n_in_sample]
        X = OLS.add_constant(self.price_b[:self.n_in_sample]) if \
            include_constant else self.price_b[:self.n_in_sample]

        # Fit regression
        OLS.fit(y, X)
        self.OLS: MultivariateLinearRegression = OLS

        summary_table = OLS.summary()

        # Determine residuals across entire period and format output
        if include_constant:
            index = ["Constant", self.ticker_b]
            residuals = self.price_a - self.price_b * OLS.coefficients[-1] \
                - OLS.coefficients[0]
        else:
            index = [self.ticker_b]
            residuals = self.price_a - self.price_b * OLS.coefficients[-1]
        summary_table.insert(0, "Regressor", index)
        summary_table.insert(0, "Regressand", self.ticker_a)

        # Assign attributes
        self.residuals: pd.Series = pd.Series(residuals)
        self.residuals.name = "Residual"
        self.b_hedge_ratio = OLS.coefficients[-1]
        self.b_coint: np.ndarray = np.hstack([1.0, -self.b_hedge_ratio])
        self.include_constant = True

        return summary_table

    def plot_timeseries(self):
        """
        Plot 4 charts for raw prices, normalised prices, regressed prices
        and the resulting residual.
        """
        plt.style.use("seaborn-v0_8")

        # Set up subplots for 2x2 area
        fig, ax = plt.subplots(nrows=2, ncols=2)

        fig.set_figheight(8)
        fig.set_figwidth(8)

        # Format x axis (date) to have exactly 5 tick marks
        for axes in ax.flatten():
            axes.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
            axes.xaxis.set_major_locator(MaxNLocator(nbins=5))

        # Raw Prices plot
        ax[0][0].plot(self.raw_price_a, label=self.ticker_a, linewidth=1)
        ax[0][0].plot(self.raw_price_b, label=self.ticker_b, linewidth=1)
        ax[0][0].legend()
        ax[0][0].title.set_text("Raw Prices")

        # Normalised plot
        ax[0][1].plot(self.price_a, linewidth=1)
        ax[0][1].plot(self.price_b, linewidth=1)
        ax[0][1].title.set_text("Normalised Prices")

        # Normalised and regressed plot
        if self.include_constant:
            plot_b = self.price_b * self.b_hedge_ratio + \
                self.OLS.coefficients[0]
        else:
            plot_b = self.price_b * self.b_hedge_ratio
        ax[1][0].plot(self.price_a, linewidth=1)
        ax[1][0].plot(plot_b, linewidth=1)
        ax[1][0].title.set_text("Regressed Prices")
        self._overlay_live_start_date_plot(ax[1][0])

        # Residual plot
        ax[1][1].plot(self.residuals, label="Residual", linewidth=1)
        ax[1][1].title.set_text("Residual")
        self._overlay_live_start_date_plot(ax[1][1])
        ax[1][1].legend()

        plt.show()

    def _overlay_live_start_date_plot(self, ax):
        """
        Overlay graph with vertical line to indicate where train ends and
        test begins.

        Parameters
        ----------
        ax
            Axes to overlay live start date vertical line onto
        """
        if self.live_start_date:
            ax.axvline(x=pd.to_datetime(self.live_start_date),
                       color="purple", linewidth=0.5,
                       linestyle=(0, (5, 10)), label="Live Start Date")

    def is_residual_stationary(self, cadf_include_constant=True):
        """
        Check if residual is stationary via the Augmented Dickey Fuller test.

        Parameters
        ----------
        adf_include_constant: bool
            Whether a constant term should be included in the OLS regression
            for ADF stationarity testing.

        Returns
        -------
        ADF Summary: pd.DataFrame
            Details stationarity test summary statistics.
        """
        # Initialise a CADF class
        cadf = ADF()

        # Test for stationarity
        coint_n_timeseries = 2  # 2 as this is bivariate Engle-Granger
        cadf_summary = cadf.stationarity_test(
            self.residuals.iloc[:self.n_in_sample], coint_n_timeseries,
            include_constant=cadf_include_constant)

        return cadf_summary

    def check_error_correction_model_mean_reversion(
            self, reverse_regression: bool = False) -> pd.DataFrame:
        """
        Construct the Error Correction Model to illustrate the short run and
        long run relationship between two timeseries.

        Parameters
        ----------
        reverse_regression: bool
            Regress ticker_b on ticker_a i.e. plugging in the "wrong way"
            residuals.

        Returns
        -------
        OLS Summary: pd.DataFrame
            Summary of error correction model

        """
        # Concatenate series then difference / lag as required
        rhs = pd.concat([self.price_a, self.price_b, self.residuals], axis=1)
        rhs = rhs.iloc[:self.n_in_sample]
        rhs.columns = [self.ticker_a, self.ticker_b, "Residuals"]

        rhs[f"Δ{self.ticker_a}"] = rhs[self.ticker_a].diff()
        rhs[f"Δ{self.ticker_b}"] = rhs[self.ticker_b].diff()
        rhs["(Lag 1, Residuals)"] = rhs["Residuals"].shift(1)

        rhs.dropna(inplace=True)

        # Construct LHS (dependent) and RHS (independent) for regression
        if not reverse_regression:
            lhs = rhs[f"Δ{self.ticker_a}"]
            rhs.drop(columns=[self.ticker_a, self.ticker_b, "Residuals",
                              f"Δ{self.ticker_a}"], inplace=True)
        else:  # reverse regression is True
            lhs = rhs[f"Δ{self.ticker_b}"]
            rhs.drop(columns=[self.ticker_a, self.ticker_b, "Residuals",
                              f"Δ{self.ticker_b}"], inplace=True)

        # Regress and format
        OLS = MultivariateLinearRegression()
        OLS.fit(lhs, rhs)
        OLS_summary = OLS.summary()
        OLS_summary.insert(0, "Regressor", rhs.columns)
        OLS_summary.insert(0, "Regressand", lhs.name)
        OLS_summary["Significant at 5%"] = OLS_summary["p-value (t-dist)"] \
            < 0.05

        return OLS_summary

    def fit_to_ornstein_uhlenbeck_sde(self):
        """
        Fit the residual to an Ornstein-Uhlenbeck stochastic differential
        equation.
        Notably, it calculates mu_e and sigma_eq
        """
        # Fit the residual to itself via an AR(1) process.
        AR = VectorAutoRegressiveModel()
        AR.fit(self.residuals.iloc[:self.n_in_sample], lags=1)
        AR_residual_stats = AR.summary()

        # Extract AR(1) fitted constant and lag=1 coefficient.
        # We follow the same naming convention as in lectures.
        C = AR.coefficients[0]  # AR(1) fitted constant
        B = AR.coefficients[1]  # AR(1) fitted lag=1 coefficient

        # Assumes daily timestep for data
        tau = 1/252

        # Speed of mean reversion
        theta = - np.log(B) / tau
        print(f"Theta: {theta:.4f}")

        # Half-life in yearfrac space
        H = np.log(2) / theta
        print(f"\nHalf-life in years: {H:.4f} years")
        print(f"Half-life in working days: {H/tau:.4f} days")

        # Equilibrium level of the residual
        self.mu_e = C / (1 - B)
        print(f"\nEquilibrium level μ_e: {self.mu_e}")

        # Compare OU fitted mean to AR(1) fitting constant/intercept
        print((f"Equilibirum level μ_e can be compared to the AR(1) "
               f"fitting intercept: {C}"))

        # Calculating diffusion terms
        sse = np.sum(AR.residuals ** 2)
        print(f"\nSum Squared Errors: {sse}")

        numerator = sse * tau  # scaled sum of squared residuals
        denominator = 1 - np.exp(-2 * theta * tau)
        self.sigma_eq = np.sqrt(numerator / denominator)
        sigma_ou = self.sigma_eq * np.sqrt(2 * theta)

        # Print derived parameter values
        print(f"\nAnnualised Variance: {numerator}")
        print(f"Diffusion in Ornstein-Uhlenbeck SDE (sigma_ou): {sigma_ou}")
        print((f"Diffusion in equilibrium to dictate entry trade signals "
               f"(sigma_eq): {self.sigma_eq}"))
        print((f"\nDiffusion of sample residuals (note the difference): "
               f"{AR.residuals.std()}"))

    def optimise_trading_strategy(self):
        """
        Given mu_e and sigma_eq, generate a mean reverting trading strategy.

        Returns
        -------
        z_table: pd.DataFrame
            Depicts total return and total trades under different Z
        df_optimal_trades: pd.DataFrame
            Trading strategy DataFrame for the optimal Z
        """
        # Optimisation for Z via grid-search
        zs = [x/100 for x in range(30, 145, 5)]
        n_trades = []
        cum_return = []

        # Get total return and total trades for each element in grid search
        for z in zs:
            df_backtest = self.create_backtest_for_z(z)
            df_backtest = self.evaluate_backtest_for_z(z, df_backtest)

            # Get total return and total trades from the training dataset
            # 2 indices before due to zero indexing and losing one row of data
            # with dropna
            trades = df_backtest["CumTrades"].iloc[self.n_in_sample - 2]
            n_trades.append(trades)

            rets = df_backtest["CumReturn"].iloc[self.n_in_sample - 2]
            cum_return.append(rets)

        # Format output
        z_table = pd.DataFrame({
            "Z": zs,
            "Total Trades": n_trades,
            "Total Return": cum_return
        })

        # Find Z with highest total return
        max_return = z_table.iloc[z_table["Total Return"].idxmax()]
        optimal_z = max_return.Z

        if self.live_start_date:
            print(f"Maximum return as at {self.live_start_date} occurs with "
                  f"Z={optimal_z}")
        else:
            print(f"Maximum return occurs with Z={optimal_z}")

        # Run strategy with optimal Z to obtain optimal trading df 
        df_optimal_trades = self.create_backtest_for_z(optimal_z)
        df_optimal_trades = self.evaluate_backtest_for_z(
            optimal_z, df_optimal_trades)

        self.optimal_strategy = df_optimal_trades

        return z_table, df_optimal_trades

    def create_backtest_for_z(self, z: float):
        """
        Create backtest under a given Z for entry trade signals.

        Parameters
        ----------
        z: float
            Number of standard deviations away from equilibirum level to enter
            the cointegrated trade.

        Returns
        -------
        backtest: pd.DataFrame
            Backtest of trades for a given Z.
        """
        def __check_breaches(row: pd.Series) -> str:
            """
            Local function as is specific to evaluating Z.
            Check whether UpperBreach or LowerBreach is true.

            Parameters
            ----------
            row: pd.Series
                Row of a dataframe containing columns LowerBreach and 
                UpperBreach.

            Returns
            -------
            Spread position: Literal["Long", "Short"]
                Spread position with respect to lower and upper bounds.
                Long if LowerBreach is true.
                Short if UpperBreach is true.
            """
            if row["LowerBreach"]:
                return "Long"
            elif row["UpperBreach"]:
                return "Short"
            else:
                return "Inactive"

        def __update_position(row: pd.Series, prev_position: str) -> str:
            """
            Local function as is specific to evaluating Z.
            Check if residual breaches trade exit signal.

            Parameters
            ----------
            row: pd.Series
                Row of a dataframe containing columns "Residual" and 
                "EqResidual".
            prev_position: str
                Latest spread positioning i.e. Long, Short or Inactive.

            Returns
            -------
            Spread position: str
                Inactive if the trade is exited or position remains inactive.
                Prevailing position if nothing is breached.
            """
            if prev_position == "Long":
                if row["Residual"] > row["UpperBound"]:
                    return "Short"  # can go directly from long to short
                elif row["Residual"] > row["EqResidual"]:
                    return "Inactive"  # exit trade
                else:
                    return "Long"
            elif prev_position == "Short":
                if row["Residual"] < row["LowerBound"]:
                    return "Long"  # can go directly from short to long
                elif row["Residual"] < row["EqResidual"]:
                    return "Inactive"  # exit trade
                else:
                    return "Short"
            else:  # prev_position is Inactive
                return __check_breaches(row)

        # Construct dataframe for trading strategy.
        z_upper_bound = self.mu_e + z * self.sigma_eq
        z_lower_bound = self.mu_e - z * self.sigma_eq
        df = pd.DataFrame(self.residuals.copy(deep=True))
        df["EqResidual"] = self.mu_e
        df["UpperBound"] = z_upper_bound
        df["LowerBound"] = z_lower_bound

        # Breaches of upper and lower bounds hence generating a trading signal.
        df["UpperBreach"] = df["Residual"].ge(df["UpperBound"])
        df["LowerBreach"] = df["Residual"].le(df["LowerBound"])

        # Generate list for spread positioning time series.
        # Possible positioning is Long / Short / Inactive.
        # Long spread position is long 1 ticker_a and short hedging ratio
        # ticker_b.
        position_list = []
        for index_dt, row in df.iterrows():
            # First day
            if not position_list:
                position = __check_breaches(row)
            # After first day
            else:
                prev_position = position_list[-1]
                position = __update_position(row, prev_position)
            # Add to position list
            position_list.append(position)

        # Positioning timeseries
        df["Position"] = position_list

        # Positioning for previous day timeseries i.e. start of current day
        # position
        df["Position_t-1"] = df["Position"].shift(1, fill_value="Inactive")

        df["IsPositionChanged"] = df["Position_t-1"] != df["Position"]

        # Edge case for setting IsPositionChanged=True if we begin with an
        # active position.
        # Have to change top 2 rows as the top row is dropped in
        # evaluate_backtest_for_z().
        first = df.index[0]
        second = df.index[1]
        df.at[first, "IsPositionChanged"] = False if \
            df.at[first, "Position"] == "Inactive" else True
        df.at[second, "IsPositionChanged"] = False if \
            df.at[second, "Position"] == "Inactive" else True

        # EnterLong is (long ticker_a x 1) and (short ticker_b x hedging ratio)
        df["EnterShort"] = (df["IsPositionChanged"] == True) & \
            (df["Position"] == "Short")
        df["EnterLong"] = (df["IsPositionChanged"] == True) & \
            (df["Position"] == "Long")

        # Edge cases for when we go from a short position to long position on
        # same day and vice versa
        df["ExitTrade"] = ((df["IsPositionChanged"] == True) &
                           (df["Position"] == "Inactive") |
                           (df["Position_t-1"] == "Short") &
                           (df["Position"] == "Long") |
                           (df["Position_t-1"] == "Long") &
                           (df["Position"] == "Short"))

        return df

    def plot_backtest(self, df: pd.DataFrame, trade_markers: bool = False):
        """
        Plot backtest of residual trading strategy.

        Parameters
        ----------
        df: pd.DataFrame
            Trading strategy dataframe output from self.create_backtest_for_z()
            Contains the spread timeseries and the trading signals
        trade_markers: bool
            Overlay markers for trade realized trades
        """
        # Plot residual and trading bounds
        plt.plot(df["Residual"], linewidth=1)
        plt.axhline(y=df["EqResidual"].iloc[0], color="green", linestyle="--")
        plt.axhline(y=df["LowerBound"].iloc[0], color="orange", linestyle="--")
        plt.axhline(y=df["UpperBound"].iloc[0], color="red", linestyle="--")

        enter_long = df[df["EnterLong"]]
        enter_short = df[df["EnterShort"]]
        exit_trade = df[df["ExitTrade"]]

        # Plot trade markers
        if trade_markers:
            plt.scatter(exit_trade.index, exit_trade.Residual,
                        color="green", label="ExitTrade", marker="x")
            plt.scatter(enter_long.index, enter_long.Residual,
                        color="orange", label="EnterLong", marker="x")
            plt.scatter(enter_short.index, enter_short.Residual,
                        color="red", label="EnterShort", marker="x")

        self._overlay_live_start_date_plot(plt)

        if trade_markers or self.live_start_date:
            plt.legend()

        plt.show()

    def evaluate_backtest_for_z(self, z: float, df: pd.DataFrame):
        """
        Evaluate backtest under a given Z for entry trade signals.

        Parameters
        ----------
        z: float
            Number of standard deviations away from equilibirum level to enter
            the cointegrated trade.
        df: pd.DataFrame
            Contains backtest trade data.

        Returns
        -------
        Backtest performance: pd.DataFrame
            Contains portfolio return.
        """
        def calculate_portfolio_return(row):
            """
            Calculate portfolio weighted average return
            """
            # Positioning
            period_start_position = row["Position_t-1"]

            # Returns array
            period_returns = np.array([
                row[f"{self.ticker_a}_returns"],
                row[f"{self.ticker_b}_returns"]
            ])

            # Dot product for weighted return
            if period_start_position == "Inactive":
                return 0
            elif period_start_position == "Long":
                return np.dot(period_returns, self.b_coint)
            else:  # period_start_position == "Short"
                return -np.dot(period_returns, self.b_coint)

        df = df.copy(deep=True)

        # Include raw, normalised prices & arithmetic returns
        df[self.ticker_a] = self.price_a
        df[self.ticker_b] = self.price_b
        df[f"{self.ticker_a}_returns"] = df[self.ticker_a].pct_change()
        df[f"{self.ticker_b}_returns"] = df[self.ticker_b].pct_change()
        df[f"{self.ticker_a}_cum_returns"] = (
            1 + df[f"{self.ticker_a}_returns"]).cumprod() - 1
        df[f"{self.ticker_b}_cum_returns"] = (
            1 + df[f"{self.ticker_b}_returns"]).cumprod() - 1

        # Benchmark prices and returns
        if self.benchmark:
            df["Benchmark"] = self.price_benchmark
            df["BenchmarkReturn"] = df["Benchmark"].pct_change()

        df.dropna(inplace=True)

        # Portfolio return from weighted return of underlying holdings
        df["PortfolioReturn"] = df.apply(lambda x:
                                         calculate_portfolio_return(x), axis=1)

        # Cumulative return
        df["CumReturn"] = (1+df["PortfolioReturn"]).cumprod() - 1

        # Cumulative executed trades
        df["CumTrades"] = df["ExitTrade"].eq(True).cumsum()

        return df

    def create_pyfolio_returns_tear_sheet(self, df: pd.DataFrame):
        """
        Use pyfolio-reloaded tear sheet functionality.

        Parameters
        ----------
        df: pd.DataFrame
            Dataframe containing trading strategy returns
        """
        # If split into train/test periods, display returns for
        # underlying securities and benchmark
        if self.live_start_date:
            self.create_out_sample_summary(df)

        if self.benchmark:
            create_returns_tear_sheet(
                df["PortfolioReturn"], benchmark_rets=df["BenchmarkReturn"],
                live_start_date=self.live_start_date)
        else:
            create_returns_tear_sheet(
                df["PortfolioReturn"], live_start_date=self.live_start_date)

    def create_out_sample_summary(self, df: pd.DataFrame):
        """
        Get cumulative returns of underlying stocks and benchmark across
        the test dataset period

        Parameters
        ----------
        df: pd.DataFrame
            Dataframe containing security returns
        """
        out_sample_dict = {}

        # Select the relevant rows / dates to calcualte returns off of
        start = df.iloc[0]
        live_start = df.loc[self.live_start_date]
        end = df.iloc[-1]

        # List of securities to iteerate through
        underlyings = [self.ticker_a, self.ticker_b]
        if self.benchmark:
            underlyings.append("Benchmark")

        for x in underlyings:
            # Generate cumulative returns across the training, test and
            # entire period
            in_sample_cum_rets = live_start[x] / start[x] - 1
            out_sample_cum_rets = end[x] / live_start[x] - 1
            all_cum_rets = end[x] / start[x] - 1

            out_sample_dict[f"{x} cumulative returns"] = [
                in_sample_cum_rets, out_sample_cum_rets, all_cum_rets]

        # Create and format DataFrame
        df = pd.DataFrame(out_sample_dict)
        df.index = ["In-sample", "Out-of-sample", "All"]
        df = df.T

        display(df)

    def plot_sp500_xs_rets_rolling_beta(self, df_optimal_trades: pd.DataFrame):
        """
        Plot rolling beta with respect to S&P 500 excess returns.
        S&P 500 yahoo finance ticker is ^SPX.
        Risk free proxy (1-month T bill rate) yahoo finance ticker is ^IRX.

        Parameters
        ----------
        df_optimal_trades: pd.DataFrame
            DataFrame containing trading strategy returns
        """
        # Get S&P500 data
        sp500 = self._get_yf_data("^SPX").Close
        sp500.name = "S&P500"
        sp500.index = sp500.index.date

        # Get risk free rate data
        rf = self._get_yf_data("^IRX").Close
        rf.name = "RiskFreeRate"
        rf.index = rf.index.date

        df = pd.concat([sp500, rf], axis=1)

        # Transform annual risk-free rate into a decimal
        df["RiskFreeRate"] = df["RiskFreeRate"] / 100

        # Transform rfr into daily rate assuming 252 trading days in year
        df["DailyRiskFreeRate"] = df["RiskFreeRate"] / 252

        # Get S&P500 daily arithmetic returns
        df["S&P500_returns"] = df["S&P500"].pct_change()

        df.dropna(inplace=True)

        # Compute excess returns
        df["S&P500_excess_returns"] = (df["S&P500_returns"] -
                                       df["DailyRiskFreeRate"])

        portfolio_return = df_optimal_trades["PortfolioReturn"].copy()
        portfolio_return.index = portfolio_return.index.date

        # Merge cointegrated strategy returns dataframe with
        # S&P500 excess returns
        df = df.join(portfolio_return, how="left")

        # Calculate rolling beta for each window size
        windows = [126, 252]
        for window in windows:
            rolling_cov = (df["PortfolioReturn"]
                           .rolling(window)
                           .cov(df["S&P500_excess_returns"]))
            rolling_var = (df["S&P500_excess_returns"]
                           .rolling(window)
                           .var())
            df[f"RollingBeta_{window}_days"] = rolling_cov / rolling_var

            plt.plot(df[f"RollingBeta_{window}_days"],
                     label=f"{window} days window", linewidth=1)

        # Plot mean 6 month window beta
        plt.axhline(y=df["RollingBeta_126_days"].mean(),
                    linewidth=0.5, linestyle="dashed", label="126 days mean")

        self._overlay_live_start_date_plot(plt)

        plt.title("Rolling Beta: Strategy vs S&P500 Excess Returns")
        plt.ylabel("Beta")
        plt.ylim(-1, 1)
        plt.legend()
        plt.show()


# Debug this Python file to step through logic
if __name__ == "__main__":
    ticker_a = "V"
    ticker_b = "MA"
    start_date = "2020-01-01"
    end_date = "2024-11-29"
    benchmark = "^SPX"
    EG = BivariateEngleGranger()
    EG.initialise_single_procedure(
        ticker_a, ticker_b, start_date, end_date, benchmark=benchmark)
    EG.run_single_procedure()
