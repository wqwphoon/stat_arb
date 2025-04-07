import datetime as dt
import logging

from dash import Dash, html

from stat_arb.model.bivariate_engle_granger import BivariateEngleGranger
from stat_arb.model.data import DataHandlerEnum

logger = logging.getLogger("stat_arb")


def app_main():
    logger.info("Configuring Dash instance...")

    app = Dash()

    app.layout = [html.Div(children="Hello world")]

    # ticker_a = "MA"
    # ticker_b = "V"
    # start = dt.datetime(2020, 1, 1)
    # end = dt.datetime(2025, 1, 8)
    # live = dt.datetime(2025, 1, 6)
    # data_enum = DataHandlerEnum.SIMULATED
    # model = BivariateEngleGranger(ticker_a, ticker_b, start, end, live, data_enum)
    # model.run()

    pass
