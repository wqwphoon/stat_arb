import datetime as dt

import pandas as pd
import pytest

from stat_arb.model.data_handler.yahoo_finance_data_handler import YahooFinanceDataHandler

START_2025 = "2025-01-01"
DELTA_WEEK_2025 = "2025-01-08"


def test_empty_ticker_list():
    with pytest.raises(ValueError):
        data = YahooFinanceDataHandler([], START_2025, DELTA_WEEK_2025)
        data.get_close_prices()


def test_spx_jan_2025_with_date_str():
    data = YahooFinanceDataHandler(["^SPX"], START_2025, DELTA_WEEK_2025)
    data = data.get_close_prices()
    assert isinstance(data, pd.DataFrame)
    assert not data.empty


def test_spx_jan_2025_with_datetime():
    start = dt.datetime.strptime(START_2025, "%Y-%m-%d")
    end = dt.datetime.strptime(DELTA_WEEK_2025, "%Y-%m-%d")
    data = YahooFinanceDataHandler(["^SPX"], start, end)
    data = data.get_close_prices()
    assert isinstance(data, pd.DataFrame)
    assert not data.empty


def test_spx_jan_2025_with_str_ticker():
    data = YahooFinanceDataHandler("^SPX", START_2025, DELTA_WEEK_2025)
    data = data.get_close_prices()
    assert isinstance(data, pd.DataFrame)
    assert not data.empty


def test_multiple_jan_2025():
    tickers = ["^SPX", "^FTSE"]
    data = YahooFinanceDataHandler(tickers, START_2025, DELTA_WEEK_2025)
    data = data.get_close_prices()
    assert isinstance(data, pd.DataFrame)
    assert not data.empty
    assert set(data.columns.get_level_values(0)) == set(tickers)


def test_invalid_date_ranges():
    with pytest.raises(ValueError):
        YahooFinanceDataHandler(["^SPX"], DELTA_WEEK_2025, START_2025)
