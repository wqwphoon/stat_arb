import datetime as dt
from typing import Sequence

from stat_arb.model.data import DataHandlerEnum, DataHandlerFactory
from stat_arb.model.statistics import (
    CointegratedAugmentedDickeyFuller,
    CointegratedAugmentedDickeyFuller_Results,
    ErrorCorrectionModel,
    ErrorCorrectionModel_Results,
    Regressor,
)
from stat_arb.model.trading_strategy import OrnsteinUhlenbeckSDE, OrnsteinUhlenbeckSDE_Results


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

        stationary: CointegratedAugmentedDickeyFuller_Results = (
            CointegratedAugmentedDickeyFuller.test_stationarity(resids, k_vars=2)
        )

        ecm: ErrorCorrectionModel_Results = ErrorCorrectionModel.fit(
            normalised[self.ticker_a], normalised[self.ticker_b], resids
        )

        long_run = ecm.is_long_run_mean_reverting()

        ou: OrnsteinUhlenbeckSDE_Results = OrnsteinUhlenbeckSDE(resids).fit_to_sde()

        pass

    def get_data(self):
        data = DataHandlerFactory.create_data_handler(
            self.data_handler_enum, [self.ticker_a, self.ticker_b], self.start_date, self.end_date
        )

        self.close_prices = data.get_close_prices()

        return self.close_prices

    def get_residual(self) -> Sequence[float]:
        self.resids = Regressor().get_residuals(
            self.close_prices[self.ticker_a], self.close_prices[self.ticker_b]
        )

        return self.resids

    def test_cadf(self) -> bool:
        cadf = CointegratedAugmentedDickeyFuller.test_stationarity(self.resids, k_vars=2)
        return cadf.significant_at_five_pct()

    def test_ecm(self) -> bool:
        ecm = ErrorCorrectionModel.fit(
            self.close_prices[self.ticker_a], self.close_prices[self.ticker_b], self.resids
        )
        return ecm.is_long_run_mean_reverting()


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
