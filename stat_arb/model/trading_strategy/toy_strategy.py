import pandas as pd

from stat_arb.model.trading_strategy.strategy import TradingStrategy


class ToyStrategy(TradingStrategy):
    def __init__(self, x: pd.Series) -> None:
        self.x = x  # spread

    def z_score_spread(self) -> pd.Series:
        mu = self.x.mean()
        sigma = self.x.std()

        z_score_spread = (self.x - mu) / sigma

        return z_score_spread
