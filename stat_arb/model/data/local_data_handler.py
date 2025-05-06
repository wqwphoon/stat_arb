import datetime as dt
import logging
import sqlite3

import pandas as pd

from stat_arb.model.config import DB
from stat_arb.model.data.data_handler import BaseDataHandler

logger = logging.getLogger(__name__)


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
        conn = sqlite3.connect(DB)
        logger.info(f"Connected to database: {DB}")

        dfs = []
        for ticker in self.tickers:
            df: pd.DataFrame = pd.read_sql_query(
                f"""SELECT Date, Close FROM {ticker} WHERE
                (Date >= '{self.start_date.strftime("%Y-%m-%d")}') AND
                (Date <= '{self.end_date.strftime("%Y-%m-%d")}')
                """,
                conn,
            )

            logger.info(f"Queried local database for ticker: {ticker}")

            df.set_index("Date", inplace=True)

            dfs.append(df)

        conn.close()
        logger.info(f"Disconnected from database: {DB}")

        df = pd.concat(dfs, axis=1, join="outer")

        # clean gaps in timeseries with ffill
        df.ffill(inplace=True)

        df.index = [pd.to_datetime(date) for date in df.index]

        df.columns = self.tickers

        return df

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
