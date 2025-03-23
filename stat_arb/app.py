import logging

from stat_arb.model.data_handler import DataHandler


def main():
    logger = logging.getLogger("stat_arb.log")
    # logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # StreamHandler for console output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # FileHandler for file output
    file_handler = logging.FileHandler("stat_arb.log", mode="a")
    file_handler.setLevel(logging.DEBUG)

    # Define log format
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Example log messages
    logger.info("Start Stat Arb app...")

    DataHandler("MSFT", "2025-01-01", "2025-01-08").get_close_prices()

    pass


if __name__ == "__main__":
    main()
    pass
