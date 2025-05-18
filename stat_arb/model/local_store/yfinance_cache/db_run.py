import datetime as dt

from stat_arb.model.local_store.yfinance_cache import store_sp500_data


def main():
    dt_start = dt.datetime(2000, 1, 1)
    dt_end = dt.datetime.today() - dt.timedelta(1)

    store_sp500_data(dt_start, dt_end)
