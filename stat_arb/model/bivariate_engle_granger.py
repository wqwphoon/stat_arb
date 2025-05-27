import datetime as dt
import logging

import numpy as np
import pandas as pd

from stat_arb.model.data import DataHandlerEnum, DataHandlerFactory
from stat_arb.model.statistics import (
    CointegratedAugmentedDickeyFuller,
    CointegratedAugmentedDickeyFuller_Results,
    ErrorCorrectionModel,
    ErrorCorrectionModel_Results,
    Regressor,
)
from stat_arb.model.trading_strategy import (
    OrnsteinUhlenbeckSDE,
    OrnsteinUhlenbeckSDE_Results,
    StrategyEnum,
    ToyStrategy,
    TradingStrategy,
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

    def run(self):
        data = DataHandlerFactory.create_data_handler(
            self.data_handler_enum, [self.ticker_a, self.ticker_b], self.start_date, self.end_date
        )

        normalised = data.get_normalised_close_prices()

        regressor = Regressor()

        resids = regressor.get_residuals(
            normalised[self.ticker_a], normalised[self.ticker_b], with_constant=True
        )

        stationary: CointegratedAugmentedDickeyFuller_Results = (  # noqa: F841
            CointegratedAugmentedDickeyFuller.test_stationarity(resids, k_vars=2)
        )

        ecm: ErrorCorrectionModel_Results = ErrorCorrectionModel.fit(
            normalised[self.ticker_a], normalised[self.ticker_b], resids
        )

        long_run = ecm.is_long_run_mean_reverting()  # noqa: F841

        ou: OrnsteinUhlenbeckSDE_Results = OrnsteinUhlenbeckSDE(resids).fit_to_sde()  # noqa: F841

        strategy = ToyStrategy(
            resids, normalised[self.ticker_a], normalised[self.ticker_b], regressor.get_beta()
        )

        strategy.backtest()
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

    def get_residual(self) -> np.ndarray:

        logger.info(f"tickers get_residual {self.ticker_a} {self.ticker_b}")

        self.regressor = Regressor()

        self.resids = self.regressor.get_residuals(
            self.close_prices[self.ticker_a], self.close_prices[self.ticker_b]
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
                raise NotImplementedError
            case StrategyEnum.OrnsteinUhlenbeckSDEFit:
                raise NotImplementedError

        self.strategy = strategy(
            self.resids,
            self.close_prices[self.ticker_a],
            self.close_prices[self.ticker_b],
            self.regressor.get_beta(),
        )

        return self.strategy

    def backtest(self, strategy_type: StrategyEnum, strategy_inputs) -> pd.DataFrame:
        strategy: TradingStrategy = self.trading_strategy_factory(strategy_type)
        # refactor factory / backtest functions. there is some sequencing requirement here

        return self.strategy.backtest(strategy_inputs)


if __name__ == "__main__":
    ticker_a = "MA"
    ticker_b = "V"
    start = dt.datetime(2020, 1, 1)
    end = dt.datetime(2025, 1, 8)
    live = dt.datetime(2025, 1, 6)
    data_enum = DataHandlerEnum.SIMULATED
    model = BivariateEngleGranger(ticker_a, ticker_b, start, end, live, data_enum)
    model.run()
    pass
