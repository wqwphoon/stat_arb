from abc import ABC, abstractmethod

import pandas as pd


class TradingStrategyResults:
    def __init__(self, backtest: pd.DataFrame):
        self._backtest = backtest

    def get_backtest(self):
        return self._backtest

    def get_cum_return(self):
        return self._backtest.iloc[-1]["Cumulative_return"]

    def get_sharpe_ratio(self): ...


class TradingStrategy(ABC):
    @abstractmethod
    def backtest(self, inputs) -> TradingStrategyResults:
        pass
