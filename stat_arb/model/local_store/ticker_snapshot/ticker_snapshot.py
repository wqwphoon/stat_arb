import datetime as dt
import logging
from pathlib import Path

import pandas as pd
import yaml

from stat_arb.model.data.data_handler_enum import DataHandlerEnum

logger = logging.getLogger(__name__)

SP500_CONSTITUENTS = r"https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

FILE_PREFIX = "sp500_tickers_"


def main() -> None:
    update_local_sp500_tickers()


def get_tickers(enum: DataHandlerEnum) -> list[str]:
    if enum == DataHandlerEnum.YAHOO:
        return get_sp500_tickers()
    else:
        return get_local_sp500_tickers()


def get_sp500_tickers() -> list[str]:
    logger.info("Web scraping S&P500 tickers from wiki...")
    return pd.read_html(SP500_CONSTITUENTS)[0]["Symbol"].to_list()


def get_local_sp500_tickers() -> list[str]:
    latest_store = get_latest_file()

    with open(latest_store, "r") as f:
        logger.info(f"Reading from file: {f.name}")
        data = yaml.safe_load(f)

    return data["tickers"]


def get_latest_file() -> Path:
    dir = Path(__file__).parent
    files = list(dir.glob(FILE_PREFIX + "*.yaml"))

    return max(files, key=extract_date)


def extract_date(path: Path) -> dt.datetime:
    date_str = path.stem.split("_")[-1]
    return dt.datetime.strptime(date_str, "%Y%m%d")


def update_local_sp500_tickers() -> None:
    """Update local yaml store of S&P500 tickers"""
    dt_str = dt.datetime.strftime(dt.date.today(), "%Y%m%d")
    filename = FILE_PREFIX + dt_str + ".yaml"
    path = Path(__file__).parent / filename

    tickers = get_sp500_tickers()
    with open(path, "w") as f:
        logger.info(f"Writing to file: {f.name}")
        yaml.dump({"tickers": tickers}, f)
