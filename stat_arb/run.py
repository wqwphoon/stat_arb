import logging

from stat_arb.app import app_main
from stat_arb.model.local_store.yfinance_cache.yfinance_cache import store_sp500_data

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

    # app_main()

    dt_start = "2000-01-01"
    dt_end = "2025-03-31"
    store_sp500_data(dt_start, dt_end)


if __name__ == "__main__":
    main()
