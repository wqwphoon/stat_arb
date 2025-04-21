import datetime as dt
import logging
from typing import Collection

import yfinance as yf

from stat_arb.model.local_store.ticker_snapshot.ticker_snapshot import get_sp500_tickers

logging.getLogger("stat_arb")


def cache_yfinance_data(tickers: Collection[str], dt_start: dt.datetime, dt_end: dt.datetime): ...


def cache_sp500_data(dt_start: dt.datetime, dt_end: dt.date) -> None:
    tickers = get_sp500_tickers()
    cache_yfinance_data(tickers, dt_start, dt_end)


if __name__ == "__main__":
    spx = yf.download("^SPX", "2020-01-01", "2021-01-01")
    pass
