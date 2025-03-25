from stat_arb.model.data_handler import DataHandler
from stat_arb.model.data_handler.simulated_data_handler import SimulatedDataHandler
from stat_arb.model.data_handler.yahoo_finance_data_handler import YahooFinanceDataHandler


class DataHandlerFactory:
    """Factory class to instantiate the appropriate DataHandler."""

    @staticmethod
    def create_data_handler(identifier: str, tickers, start_date, end_date) -> DataHandler:
        if identifier == "Yahoo":
            return YahooFinanceDataHandler(tickers, start_date, end_date)
        elif identifier == "Simulated":
            return SimulatedDataHandler(tickers, start_date, end_date)
        else:
            raise ValueError(f"Unknown data handler identifer: {identifier}")
