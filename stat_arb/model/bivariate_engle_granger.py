import datetime as dt
import logging

import pandas as pd

from stat_arb.model.data import DataHandlerEnum, DataHandlerFactory
from stat_arb.model.statistics import CointegratedAugmentedDickeyFuller, ErrorCorrectionModel, Regressor
from stat_arb.model.trading_strategy import (
    RollingWindow,
    StrategyEnum,
    ToyStrategy,
    TradingStrategy,
    TradingStrategyResults,
)

logger = logging.getLogger(__name__)


class BivariateEngleGranger:
    def __init__(
        self,
        ticker_a: str,
        ticker_b: str,
        start_date: dt.datetime,
        end_date: dt.datetime,
        live_start_date: dt.datetime,
        data_handler_enum: DataHandlerEnum,
    ):
        self.ticker_a = ticker_a
        self.ticker_b = ticker_b
        self.start_date = start_date
        self.end_date = end_date
        self.live_start_date = live_start_date
        self.data_handler_enum = data_handler_enum

    def run(self, strategy_enum: StrategyEnum, strategy_inputs):

        logger.info("Initiate Data Extraction...")

        self.data_init()

        self.get_normalised_close_prices()

        self.get_residual()

        logger.info("Initiate Statistical Tests...")

        if self.test_cadf() is True:
            logger.info("Residual is stationary at 5% significance")
        else:
            logger.info("Reidual is not stationary at 5% significance")

        if self.test_ecm() is True:
            logger.info("Residual displays long run mean reversion at 5% significance")
        else:
            logger.info("Residual absent of long run mean reversionat 5% significance")

        logger.info("Initiate Trading Strategy...")

        self.backtest(strategy_enum, strategy_inputs)

        pass

    def data_init(self) -> None:
        self.data_handler = DataHandlerFactory.create_data_handler(
            self.data_handler_enum, [self.ticker_a, self.ticker_b], self.start_date, self.end_date
        )

    def get_close_prices(self):
        if not getattr(self, "data_handler", None):
            self.data_init()

        self.close_prices = self.data_handler.get_close_prices()

        return self.close_prices

    def get_normalised_close_prices(self):
        if not getattr(self, "data_handler", None):
            self.data_init()

        self.normalised_close_prices = self.data_handler.get_normalised_close_prices()

        return self.normalised_close_prices

    def get_residual(self, use_normalised_prices=True) -> pd.Series:
        self.regressor = Regressor()

        if not use_normalised_prices:
            self.resids = self.regressor.get_residuals(
                self.close_prices[self.ticker_a], self.close_prices[self.ticker_b]
            )

        self.resids = self.regressor.get_residuals(
            self.normalised_close_prices[self.ticker_a], self.normalised_close_prices[self.ticker_b]
        )

        return self.resids

    def test_cadf(self) -> bool:
        cadf = CointegratedAugmentedDickeyFuller.test_stationarity(self.resids, k_vars=2)
        return cadf.significant_at_five_pct()

    def test_ecm(self) -> bool:
        ecm = ErrorCorrectionModel.fit(
            self.close_prices[self.ticker_a], self.close_prices[self.ticker_b], pd.Series(self.resids)
        )
        return ecm.is_long_run_mean_reverting()

    def trading_strategy_factory(self, strategy_enum: StrategyEnum) -> TradingStrategy:
        match strategy_enum:
            case StrategyEnum.ToyStrategy:
                strategy = ToyStrategy
            case StrategyEnum.RollingWindow:
                strategy = RollingWindow
            case StrategyEnum.OrnsteinUhlenbeckSDEFit:
                raise NotImplementedError

        self.strategy = strategy(
            self.resids,
            self.close_prices[self.ticker_a],
            self.close_prices[self.ticker_b],
            self.regressor.get_beta(),
        )

        return self.strategy

    def backtest(self, strategy_type: StrategyEnum, strategy_inputs) -> TradingStrategyResults:
        self.trading_strategy_factory(strategy_type)

        self.backtest_results = self.strategy.backtest(strategy_inputs)

        return self.backtest_results


if __name__ == "__main__":
    ticker_a = "MA"
    ticker_b = "V"
    start = dt.datetime(2020, 1, 1)
    end = dt.datetime(2025, 1, 8)
    live = dt.datetime(2025, 1, 6)
    data_enum = DataHandlerEnum.SIMULATED
    model = BivariateEngleGranger(ticker_a, ticker_b, start, end, live, data_enum)
    pass
