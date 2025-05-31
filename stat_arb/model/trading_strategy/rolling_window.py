import logging
from dataclasses import dataclass
from typing import Optional, Union

import numpy as np
import pandas as pd

from stat_arb.model.trading_strategy.strategy import TradingStrategy, TradingStrategyResults

logger = logging.getLogger(__name__)


@dataclass
class RollingWindowInputs:
    enter_threshold: float
    exit_threshold: float
    window_length: int


class RollingWindow(TradingStrategy):
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

    def backtest(self, inputs: Optional[RollingWindowInputs] = None) -> TradingStrategyResults:
        if inputs is None:
            inputs = RollingWindowInputs(enter_threshold=1, exit_threshold=0, window_length=30)

        self.df["Z-Score"] = (
            self.df["Residual"] - self.df["Residual"].rolling(inputs.window_length).mean()
        ) / self.df["Residual"].rolling(inputs.window_length).std()

        self.df["LongEntrySignal"] = self.df["Z-Score"] < -inputs.enter_threshold
        self.df["ShortEntrySignal"] = self.df["Z-Score"] > inputs.enter_threshold
        self.df["LongExitSignal"] = self.df["Z-Score"] > -inputs.exit_threshold
        self.df["ShortExitSignal"] = self.df["Z-Score"] < inputs.exit_threshold

        current_signal = 0
        signals = []

        for index, row in self.df.iterrows():
            match current_signal:
                case 0:
                    if row["LongEntrySignal"]:
                        new_signal = 1
                    elif row["ShortEntrySignal"]:
                        new_signal = -1
                    else:
                        new_signal = 0
                case 1:
                    if row["ShortEntrySignal"]:
                        new_signal = -1
                    elif row["LongExitSignal"]:
                        new_signal = 0
                    else:
                        new_signal = 1
                case -1:
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
