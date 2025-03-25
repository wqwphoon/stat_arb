import datetime as dt

import numpy as np
import pandas as pd

from stat_arb.model.data_handler import DataHandler


class SimulatedDataHandler(DataHandler):
    def __init__(self, tickers: list[str] | str, start_date: dt.datetime | str, end_date: dt.datetime | str):
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

        self._data: pd.DataFrame | None = None

    def get_close_prices(self) -> pd.DataFrame:
        n: int = len(self.tickers)

        period: pd.DatetimeIndex = pd.date_range(self.start_date, self.end_date)
        period: list[pd.Timestamp] = [date for date in period if self.is_weekday(date)]

        prices: np.ndarray = 1 + np.random.normal(size=[len(period), n]).cumsum(axis=0) / 100
        prices: pd.DataFrame = pd.DataFrame(prices, columns=self.tickers, index=period)

        return prices

    def is_weekday(self, date: pd.Timestamp):
        return date.dayofweek not in [5, 6]


if __name__ == "__main__":
    tickers = "^SPX"
    start_date = dt.datetime(2025, 1, 1)
    end_date = dt.datetime(2025, 1, 7)
    data = SimulatedDataHandler(tickers, start_date, end_date)
    close = data.get_close_prices()
    pass
