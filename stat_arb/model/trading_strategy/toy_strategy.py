import pandas as pd

from stat_arb.model.trading_strategy.strategy import TradingStrategy


class ToyStrategy(TradingStrategy):
    def __init__(self, x: pd.Series[float]) -> None:
        self.x = x  # spread
