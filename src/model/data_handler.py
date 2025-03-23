import datetime as dt

import pandas as pd
import yfinance as yf


class DataHandler:
    def __init__(self, tickers: list[str], start_date, end_date):
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date

        self._data: pd.DataFrame | None = None

    def _fetch_data(self):
        """Private method to fetch data from yfinance - ensures encapsulation."""
        try:
            print("Fetching data from Yahoo Finance...")
            self._data = yf.download(
                self.tickers, start=self.start_date, end=self.end_date, group_by="ticker"
            )
        except Exception as e:
            print(f"Error fetching data: {e}")
            self._data = None

    def get_full_data(self):
        """Public getter method to access data."""
        if self._data is None:  # lazy loading - could be implemented with decorator
            self._fetch_data()

        return self._data

    def get_close_prices(self):
        if self._data is None:
            self._fetch_data()

        return self._data.xs(key="Close", axis=1, level=1)


if __name__ == "__main__":
    tickers = ["AMZN"]
    start_date = dt.datetime(2025, 1, 1)
    end_date = dt.datetime(2025, 1, 7)
    data = DataHandler(tickers, start_date, end_date)
    data.get_close_prices()
    pass
