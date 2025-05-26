from abc import ABC, abstractmethod

import pandas as pd


class TradingStrategy(ABC):
    # @abstractmethod
    def read_input(self):
        pass

    @abstractmethod
    def backtest(self) -> pd.DataFrame:
        pass

    # @abstractmethod
    def get_output(self):
        pass
