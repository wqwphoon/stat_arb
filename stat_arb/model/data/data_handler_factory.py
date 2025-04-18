import logging

from stat_arb.model.data import BaseDataHandler
from stat_arb.model.data.data_handler_enum import DataHandlerEnum
from stat_arb.model.data.simulated_data_handler import SimulatedDataHandler
from stat_arb.model.data.yahoo_finance_data_handler import YahooFinanceDataHandler

logger = logging.getLogger("stat_arb")


class DataHandlerFactory:
    """Factory class to instantiate the appropriate DataHandler."""

    @staticmethod
    def create_data_handler(identifier: str, tickers, start_date, end_date) -> BaseDataHandler:
        if identifier == DataHandlerEnum.YAHOO:
            logger.info(f"Creating DataHandler type: {DataHandlerEnum.YAHOO.value}")
            return YahooFinanceDataHandler(tickers, start_date, end_date)
        elif identifier == DataHandlerEnum.SIMULATED:
            logger.info(f"Creating DataHandler type: {DataHandlerEnum.SIMULATED.value}")
            return SimulatedDataHandler(tickers, start_date, end_date)
        else:
            raise ValueError(f"Unknown data handler identifier: {identifier}")
