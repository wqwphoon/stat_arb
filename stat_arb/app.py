import datetime as dt
import logging

from stat_arb.model.bivariate_engle_granger import BivariateEngleGranger
from stat_arb.model.data import DataHandlerEnum

# Configure the logger
logger = logging.getLogger("stat_arb")
logger.setLevel(logging.DEBUG)

# StreamHandler for console output
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# FileHandler for file output
file_handler = logging.FileHandler("stat_arb.log", mode="a")
file_handler.setLevel(logging.DEBUG)

# Define log format
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers to the logger
if not logger.handlers:
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


def main():
    logger.info("Start Stat Arb app...")

    ticker_a = "MA"
    ticker_b = "V"
    start = dt.datetime(2020, 1, 1)
    end = dt.datetime(2025, 1, 8)
    live = dt.datetime(2025, 1, 6)
    data_enum = DataHandlerEnum.SIMULATED
    model = BivariateEngleGranger(ticker_a, ticker_b, start, end, live, data_enum)
    model.run()

    pass


if __name__ == "__main__":
    main()
    pass
