from dataclasses import dataclass
from typing import Literal

import pandas as pd

from stat_arb.model.trading_strategy.strategy import TradingStrategy


@dataclass
class ToyStrategyInputs:
    enter_threshold: float
    exit_threshold: float


class ToyStrategy(TradingStrategy):
    def __init__(self, x: pd.Series) -> None:
        self.x = x  # spread

    def backtest(self, inputs: ToyStrategyInputs) -> pd.DataFrame:
        df = pd.DataFrame(self.x)

        mu = self.x.mean()
        sigma = self.x.std()

        df["Z-Score"] = (df["Residual"] - mu) / sigma

        df["Signal"] = df["Z-Score"].apply(
            lambda x: self.signal(x, inputs.enter_threshold, inputs.exit_threshold)
        )

        return df

    def signal(
        self, z_score: float, enter_threshold: float, exit_threshold: float
    ) -> Literal[-1, 0, 1, None]:
        if z_score < -abs(enter_threshold):
            return 1
        elif z_score > abs(enter_threshold):
            return -1
        elif abs(z_score) < exit_threshold:
            return 0
        else:
            return None
