from abc import ABC, abstractmethod

import pandas as pd


class TradingStrategyResults:
    def __init__(self, backtest: pd.DataFrame):
        self._backtest = backtest

    def get_backtest(self):
        return self._backtest

    def get_cum_return(self):
        return self._backtest.tail(1)["Cumulative_return"]


class TradingStrategy(ABC):
    # @abstractmethod
    def read_input(self):
        pass

    @abstractmethod
    def backtest(self) -> TradingStrategyResults:
        pass
