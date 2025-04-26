import datetime as dt
import sqlite3

import pandas as pd

from stat_arb.model.data.data_handler import BaseDataHandler
from stat_arb.model.local_store.yfinance_cache.yfinance_cache import db


class LocalDataHandler(BaseDataHandler):
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

    def get_close_prices(self) -> pd.DataFrame:

        conn = sqlite3.connect(db)

        dfs = []
        for ticker in self.tickers:
            df: pd.DataFrame = pd.read_sql_query(
                f"""SELECT * FROM {ticker} WHERE
                (Date >= '{self.start_date.strftime("%Y-%m-%d")}') AND
                (Date <= '{self.end_date.strftime("%Y-%m-%d")}')
                """,
                conn,
            )

            df.set_index("Date", inplace=True)

            df.columns = [f"{ticker} | {x}" for x in df.columns]

            dfs.append(df)

        conn.close()

        df = pd.concat(dfs, axis=1, join="outer")

        # clean gaps in timeseries with ffill
        df.ffill(inplace=True)

        close_cols = [f"{x} | Close" for x in self.tickers]

        return df[close_cols]

    def get_normalised_close_prices(self) -> pd.DataFrame:
        df = self.get_close_prices()
        return df.div(df.iloc[0], axis=1)


if __name__ == "__main__":
    start = "2025-01-01"
    end = "2025-03-01"

    tickers = ["MA", "V"]

    data = LocalDataHandler(tickers, start, end)
    data.get_close_prices()
    data.get_normalised_close_prices()
    pass
