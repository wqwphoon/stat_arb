from dataclasses import dataclass
from typing import Literal, Optional

import numpy as np
import pandas as pd

from stat_arb.model.trading_strategy.strategy import TradingStrategy


@dataclass
class ToyStrategyInputs:
    enter_threshold: float
    exit_threshold: float


class ToyStrategy(TradingStrategy):
    def __init__(
        self, resids: pd.Series, price_x: pd.Series, price_y: pd.Series, beta: pd.Series | float
    ) -> None:
        self.resids = resids
        self.price_x = price_x
        self.price_y = price_y
        self.beta = self.to_series(beta)

        cols = [f"{price_x.name}_close", f"{price_y.name}_close", "Residual", "Beta"]
        self.df: pd.DataFrame = pd.concat([price_x, price_y, resids, self.beta], axis=1, keys=cols)

    def to_series(self, beta: pd.Series | float) -> pd.Series:
        if isinstance(beta, float):
            n = len(self.resids)
            return pd.Series(np.ones(shape=(n)) * beta)
        else:
            return beta

    def backtest(self, inputs: Optional[ToyStrategyInputs] = None) -> pd.DataFrame:
        if inputs is None:
            inputs = ToyStrategyInputs(enter_threshold=1, exit_threshold=0)

        mu = self.resids.mean()
        sigma = self.resids.std()

        self.df["Z-Score"] = (self.df["Residual"] - mu) / sigma

        signal = self.df["Z-Score"].apply(
            lambda x: self.signal(x, inputs.enter_threshold, inputs.exit_threshold)
        )

        signal = signal.ffill().fillna(0)

        self.df["Signal"] = signal

        self.df[f"{self.price_x.name}_returns"] = self.df[f"{self.price_x.name}_close"].pct_change()
        self.df[f"{self.price_y.name}_returns"] = self.df[f"{self.price_x.name}_close"].pct_change()

        self.df["Portfolio_return"] = self.df["Signal"].shift(1) * (
            self.df[f"{self.price_x.name}_returns"]
            - self.df["Beta"] * self.df[f"{self.price_y.name}_returns"]
        )

        self.df["Cumulative_return"] = (1 + self.df["Portfolio_return"]).cumprod()

        # drop na for first row?

        return self.df

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
