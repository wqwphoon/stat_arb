import logging

import plotly.express as px
from dash import Input, Output, callback, exceptions

from stat_arb.model.bivariate_engle_granger import BivariateEngleGranger
from stat_arb.model.data.data_handler_enum import DataHandlerEnum, get_enum_from_str
from stat_arb.model.defaults.defaults import get_tickers
from stat_arb.view.ids import IDS

logging.getLogger("stat_arb")

SINGLE_USER_INSTANCE = {}
MODEL = "model"


def get_datasource_enums():
    return [e for e in DataHandlerEnum]


def get_default_datasource_enum():
    return DataHandlerEnum.SIMULATED


@callback(
    Output(IDS.INPUTS.TICKER_A, "options"),
    Output(IDS.INPUTS.TICKER_B, "options"),
    Input(IDS.INPUTS.DATA_SOURCE, "value"),
)
def get_default_tickers(data_source_enum: DataHandlerEnum):
    tickers = get_tickers(data_source_enum)
    return tickers, tickers


@callback(
    Output(component_id=IDS.GRAPHS.PRICE_SERIES, component_property="figure"),
    Input(component_id=IDS.INPUTS.DATE_RANGE, component_property="start_date"),
    Input(component_id=IDS.INPUTS.DATE_RANGE, component_property="end_date"),
    Input(component_id=IDS.INPUTS.TICKER_A, component_property="value"),
    Input(component_id=IDS.INPUTS.TICKER_B, component_property="value"),
    Input(component_id=IDS.INPUTS.DATA_SOURCE, component_property="value"),
    Input(component_id=IDS.INPUTS.TEST_TRAIN_SPLIT, component_property="value"),
)
def generate_model_from_setup(start_date, end_date, ticker_a, ticker_b, data_source, test_train_split):
    if None in [start_date, end_date, ticker_a, ticker_b, data_source, test_train_split]:
        exceptions.PreventUpdate

    enum: DataHandlerEnum = get_enum_from_str(data_source)

    # TODO: fix for test train split start date
    model = BivariateEngleGranger(ticker_a, ticker_b, start_date, end_date, start_date, enum)

    SINGLE_USER_INSTANCE[MODEL] = model

    return px.line(model.get_data())


@callback(Output(IDS.STATISTICS.ADF_RESULT, "children"), Input(IDS.GRAPHS.RESIDUAL, "figure"))
def get_adf_result(_):
    model: BivariateEngleGranger = SINGLE_USER_INSTANCE[MODEL]
    cadf_result: bool = model.test_cadf()

    return "Stationary at 5% significance level" if cadf_result else "Not stationary at 5% significance level"


@callback(Output(IDS.STATISTICS.ECM_RESULT, "children"), Input(IDS.GRAPHS.RESIDUAL, "figure"))
def get_ecm_result(_):
    model: BivariateEngleGranger = SINGLE_USER_INSTANCE[MODEL]
    ecm_result: bool = model.test_ecm()

    return (
        "Long run mean reversion at 5% significance level"
        if ecm_result
        else "Absent of long run mean reversion at 5% significance level"
    )
