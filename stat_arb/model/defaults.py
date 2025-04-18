import pandas as pd

from stat_arb.model.data.data_handler_enum import DataHandlerEnum

SP500_CONSTITUENTS = r"https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"


def get_tickers(enum: DataHandlerEnum) -> list[str]:
    if enum == DataHandlerEnum.YAHOO:
        return get_sp500_tickers()
    else:
        return get_local_sp500_tickers()


def get_sp500_tickers() -> list[str]:
    return pd.read_html(SP500_CONSTITUENTS)[0]["Symbol"].to_list()


def get_local_sp500_tickers() -> list[str]:
    return ["SPX", "AMZN"]
