import logging

import plotly
import plotly.express as px
import plotly.subplots
from dash import Input, Output, State, callback, exceptions

from stat_arb.model.bivariate_engle_granger import BivariateEngleGranger
from stat_arb.model.data.data_handler_enum import DataHandlerEnum, get_enum_from_str
from stat_arb.model.local_store.ticker_snapshot.ticker_snapshot import get_tickers
from stat_arb.view.ids import IDS

logger = logging.getLogger(__name__)

# In-memory store for local development
# Use dcc.Store and serializable data (rather than wrapper class) for multi-user production
SINGLE_USER_INSTANCE = {}
MODEL = "model"


def get_datasource_enums():
    return [e for e in DataHandlerEnum]


def get_default_datasource_enum():
    return DataHandlerEnum.SIMULATED


@callback(
    Output(IDS.STORE_INPUTS.TICKER_A, "options"),
    Output(IDS.STORE_INPUTS.TICKER_B, "options"),
    Input(IDS.STORE_INPUTS.DATA_SOURCE, "value"),
)
def get_default_tickers(data_source_enum: DataHandlerEnum):
    tickers = get_tickers(data_source_enum)
    return tickers, tickers


@callback(
    Output(component_id=IDS.GRAPHS.PRICE_SERIES, component_property="figure"),
    Input(component_id=IDS.INPUTS.DATA_INPUT, component_property="n_clicks"),
    State(component_id=IDS.STORE_INPUTS.DATE_RANGE, component_property="start_date"),
    State(component_id=IDS.STORE_INPUTS.DATE_RANGE, component_property="end_date"),
    State(component_id=IDS.STORE_INPUTS.TICKER_A, component_property="value"),
    State(component_id=IDS.STORE_INPUTS.TICKER_B, component_property="value"),
    State(component_id=IDS.STORE_INPUTS.DATA_SOURCE, component_property="value"),
    State(component_id=IDS.STORE_INPUTS.TEST_TRAIN_SPLIT, component_property="value"),
)
def generate_model_from_setup(load, start_date, end_date, ticker_a, ticker_b, data_source, test_train_split):
    if None in [start_date, end_date, ticker_a, ticker_b, data_source, test_train_split]:
        exceptions.PreventUpdate

    enum: DataHandlerEnum = get_enum_from_str(data_source)

    # TODO: fix for test train split start date
    model = BivariateEngleGranger(ticker_a, ticker_b, start_date, end_date, start_date, enum)

    SINGLE_USER_INSTANCE[MODEL] = model

    fig = plotly.subplots.make_subplots(rows=2, cols=1)

    fig1 = px.line(model.get_close_prices(), y=[ticker_a, ticker_b], title="Raw Prices")
    fig2 = px.line(model.get_normalised_close_prices(), y=[ticker_a, ticker_b], title="Normalised Prices")

    fig.add_traces(fig1.data, rows=1, cols=1)
    fig.add_traces(fig2.data, rows=2, cols=1)

    fig.update_layout(title_text="Stock Prices")

    return fig


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
