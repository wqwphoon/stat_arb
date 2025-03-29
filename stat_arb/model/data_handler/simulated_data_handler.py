import datetime as dt

import numpy as np
import pandas as pd

from stat_arb.model.data_handler import DataHandler


class SimulatedDataHandler(DataHandler):
    def __init__(
        self,
        tickers: list[str] | str,
        start_date: dt.datetime | str,
        end_date: dt.datetime | str,
        corr: float = 0.2,
    ):
        # Perform validation of input parameters
        if not tickers:
            raise ValueError("Tickers list cannot be empty.")
        if isinstance(start_date, str):
            start_date = dt.datetime.strptime(start_date, "%Y-%m-%d")
        if isinstance(end_date, str):
            end_date = dt.datetime.strptime(end_date, "%Y-%m-%d")
        if end_date < start_date:
            raise ValueError("End date must not be before start date")
        if isinstance(tickers, str):
            tickers = [tickers]

        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date

        self.corr = corr
        self.mu = 0.06
        self.sigma = 0.2
        self.dt = 1 / 252

    def get_close_prices(self) -> pd.DataFrame:
        period: list[pd.Timestamp] = self.get_dates()

        n_period: int = len(period)
        n_ticker: int = len(self.tickers)

        prices: np.ndarray = self.simulate_gbm(n_period, n_ticker)

        prices: pd.DataFrame = pd.DataFrame(prices, columns=self.tickers, index=period)

        return prices

    def simulate_gbm(self, n_period, n_ticker) -> np.ndarray:
        rng: np.ndarray = self.get_correlated_random_numbers(n_period, n_ticker)

        prices = np.ones((n_period, n_ticker)) * 100

        for row in range(1, n_period):
            dX = np.sqrt(self.dt) * rng[row, :]
            prices[row, :] = prices[row - 1, :] * (1 + self.mu * self.dt + self.sigma * dX)

        return prices

    def get_correlated_random_numbers(self, rows, cols) -> np.ndarray:
        rand: np.ndarray = np.random.normal(size=[rows, cols])
        rand[:, 1:] = rand[:, 0].reshape((-1, 1)) * self.corr + np.sqrt(1 - self.corr**2) * rand[:, 1:]

        return rand

    def get_dates(self) -> list[pd.Timestamp]:
        period: pd.DatetimeIndex = pd.date_range(self.start_date, self.end_date)
        period: list[pd.Timestamp] = [date for date in period if self.is_weekday(date)]

        return period

    def is_weekday(self, date: pd.Timestamp) -> bool:
        return date.dayofweek not in [5, 6]

    def get_normalised_close_prices(self) -> pd.DataFrame:
        close = self.get_close_prices()
        return close.div(close.iloc[0])


if __name__ == "__main__":
    tickers = "^SPX"
    start_date = dt.datetime(2025, 1, 1)
    end_date = dt.datetime(2025, 1, 7)
    data = SimulatedDataHandler(tickers, start_date, end_date)
    close = data.get_close_prices()
    pass
