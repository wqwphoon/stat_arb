import datetime as dt
from functools import wraps

import pandas as pd
import yfinance as yf

from stat_arb.model.data_handler.data_handler import DataHandler


def lazy_load_data(func):
    """Decorator to ensure data is fetched before method execution - lazy loading"""

    @wraps(func)
    def wrapper(self, *args, force_refresh=False, **kwargs):
        if (self._data is None) or force_refresh:  # Check if refresh is required
            self._fetch_data()
        return func(self, *args, **kwargs)

    return wrapper


class YahooFinanceDataHandler(DataHandler):
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

    def _fetch_data(self) -> None:
        """Private method to fetch data from yfinance - ensures encapsulation."""
        try:
            print("Fetching data from Yahoo Finance...")
            self._data = yf.download(
                self.tickers, start=self.start_date, end=self.end_date, group_by="ticker"
            )
            pass
        except Exception as e:
            print(f"Error fetching data: {e}")
            self._data = None

    @lazy_load_data
    def get_full_data(self) -> pd.DataFrame:
        """Public getter method to access data."""
        return self._data

    @lazy_load_data
    def get_close_prices(self) -> pd.DataFrame:
        """Public getter method to access close price data."""
        return self._data.xs(key="Close", axis=1, level=1)


if __name__ == "__main__":
    tickers = "^SPX"
    start_date = dt.datetime(2025, 1, 1)
    end_date = dt.datetime(2025, 1, 7)
    data = YahooFinanceDataHandler(tickers, start_date, end_date)
    close = data.get_close_prices()
    pass
