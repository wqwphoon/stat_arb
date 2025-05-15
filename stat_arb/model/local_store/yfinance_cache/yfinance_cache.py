import datetime as dt
import logging
import sqlite3

import yfinance as yf

from stat_arb.model.config import DB
from stat_arb.model.local_store.ticker_snapshot.ticker_snapshot import get_sp500_tickers

logger = logging.getLogger(__name__)


def store_yfinance_data(tickers: list[str], dt_start: dt.datetime, dt_end: dt.datetime):
    """Streaming response to store each ticker data individually"""
    conn = sqlite3.connect(DB)
    logger.info(f"Connected to database: {DB}")

    n = len(tickers)

    for i in range(n):
        df = yf.download(
            tickers=tickers[i], start=dt_start, end=dt_end, multi_level_index=False, progress=False
        )
        df.to_sql(tickers[i], conn, if_exists="replace")
        logger.info(f"Processing ticker {int(i+1)} out of {int(n)} : {tickers[i]}")

    conn.close()
    logger.info(f"Disconnected from database: {DB}")


def store_sp500_data(dt_start: dt.datetime, dt_end: dt.datetime) -> None:
    tickers = get_sp500_tickers()
    store_yfinance_data(tickers, dt_start, dt_end)
