from dataclasses import dataclass
from typing import Literal, Optional, Union

import numpy as np
import pandas as pd

from stat_arb.model.trading_strategy.strategy import TradingStrategy, TradingStrategyResults


@dataclass
class ToyStrategyInputs:
    enter_threshold: float
    exit_threshold: float


class ToyStrategy(TradingStrategy):
    def __init__(
        self,
        resids: Union[pd.Series, np.ndarray],
        price_x: pd.Series,
        price_y: pd.Series,
        beta: pd.Series | float,
    ) -> None:
        self.resids = self.to_series(resids)
        self.price_x = price_x
        self.price_y = price_y
        self.beta = self.to_series(beta)

        cols = [f"{price_x.name}_close", f"{price_y.name}_close", "Residual", "Beta"]
        self.df: pd.DataFrame = pd.concat([price_x, price_y, self.resids, self.beta], axis=1, keys=cols)

    def to_series(self, vector: pd.Series | float | np.ndarray) -> pd.Series:
        if isinstance(vector, float):
            n = len(self.resids)
            return pd.Series(np.ones(shape=(n)) * vector)
        elif isinstance(vector, np.ndarray):
            return pd.Series(vector)
        else:
            return vector

    def backtest(self, inputs: Optional[ToyStrategyInputs] = None) -> TradingStrategyResults:
        if inputs is None:
            inputs = ToyStrategyInputs(enter_threshold=1, exit_threshold=0)

        mu = self.resids.mean()
        sigma = self.resids.std()

        self.df["Z-Score"] = (self.df["Residual"] - mu) / sigma

        self.df["LongEntrySignal"] = self.df["Z-Score"] < -ToyStrategyInputs.enter_threshold
        self.df["ShortEntrySignal"] = self.df["Z-Score"] > ToyStrategyInputs.enter_threshold
        self.df["LongExitSignal"] = self.df["Z-Score"] > -ToyStrategyInputs.exit_threshold
        self.df["ShortExitSignal"] = self.df["Z-Score"] < ToyStrategyInputs.exit_threshold

        current_signal = 0
        signals = []

        for index, row in self.df.iterrows():
            if current_signal == 0:
                if row["LongEntrySignal"]:
                    new_signal = 1
                elif row["ShortEntrySignal"]:
                    new_signal = -1
                else:
                    new_signal = 0
            elif current_signal == 1:
                if row["ShortEntrySignal"]:
                    new_signal = -1
                elif row["LongExitSignal"]:
                    new_signal = 0
                else:
                    new_signal = 1
            else:  # current_signal == -1
                if row["LongEntrySignal"]:
                    new_signal = 1
                elif row["ShortExitSignal"]:
                    new_signal = 0
                else:
                    new_signal = -1

            current_signal = new_signal
            signals.append(new_signal)

        self.df["Signal"] = signals

        self.df[f"{self.price_x.name}_returns"] = self.df[f"{self.price_x.name}_close"].pct_change()
        self.df[f"{self.price_y.name}_returns"] = self.df[f"{self.price_x.name}_close"].pct_change()

        self.df["Portfolio_return"] = self.df["Signal"].shift(1) * (
            self.df[f"{self.price_x.name}_returns"]
            - self.df["Beta"] * self.df[f"{self.price_y.name}_returns"]
        )

        self.df["Cumulative_return"] = (1 + self.df["Portfolio_return"]).cumprod()

        # drop na for first row?

        return TradingStrategyResults(self.df)

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
