from abc import ABC, abstractmethod

import numpy as np
import pandas as pd


class TradingStrategyResults:
    REQUIRED_COLUMNS = ["Residual", "Cumulative_return", "Portfolio_return"]

    def __init__(self, backtest: pd.DataFrame):
        self._validate(backtest)
        self._backtest = backtest

    def _validate(self, df):
        missing = set(self.REQUIRED_COLUMNS) - set(df.columns)
        if missing:
            raise ValueError(f"Missing fields: {missing}")

    def get_backtest(self):
        return self._backtest

    @property
    def period_return(self) -> pd.Series:
        return self._backtest["Portfolio_return"]

    @property
    def cumulative_return(self) -> pd.Series:
        return self._backtest["Cumulative_return"]

    def get_cum_return(self) -> float:
        return self.cumulative_return.iloc[-1]

    def get_sharpe_ratio(self) -> float:
        """Set risk free rate to 0 - common in practice"""
        rfr = 0
        excess_return = self.period_return - rfr

        daily_sharpe = excess_return.mean() / excess_return.std()

        annualised_sharpe = daily_sharpe * np.sqrt(252)

        return annualised_sharpe

    def get_sortino_ratio(self) -> float:
        """Set risk free rate to 0 - common in practice"""
        rfr = 0
        excess_return = self.period_return - rfr
        downside_excess_return = excess_return[excess_return < 0]

        daily_sortino = excess_return.mean() / downside_excess_return.std()

        annualised_sortino = daily_sortino * np.sqrt(252)

        return annualised_sortino

    def get_max_drawdown(self) -> float:
        rolling_max = self.cumulative_return.cummax()

        daily_drawdown = (self.cumulative_return / rolling_max) - 1

        return daily_drawdown.min()

    def get_annualised_return(self) -> float:
        trading_days = self.period_return.notna().sum()
        trading_years = trading_days / 252

        return (self.get_cum_return() ** (1 / trading_years)) - 1

    def get_annualised_vol(self) -> float:
        return self.period_return.std() * np.sqrt(252)


class TradingStrategy(ABC):
    @abstractmethod
    def backtest(self, inputs) -> TradingStrategyResults:
        pass
