import logging

import plotly.express as px
from dash import ALL, Input, Output, callback, ctx

from stat_arb.controller.callbacks import MODEL, SINGLE_USER_INSTANCE
from stat_arb.model.bivariate_engle_granger import BivariateEngleGranger
from stat_arb.model.regressor import RegressorEnum
from stat_arb.model.regressor.naive_regressor import NaiveRegressorInputs
from stat_arb.model.regressor.rolling_window_regressor import RollingWindowRegressorInputs
from stat_arb.view.ids import IDS, REGRESSION_INPUT
from stat_arb.view.regressor_layout import naive_regressor_inputs, rolling_window_regressor_inputs

logger = logging.getLogger(__name__)


def get_regressor_options():
    return [e for e in RegressorEnum]


@callback(Output(IDS.GRAPHS.RESIDUAL, "figure"), Input(IDS.REGRESSION.INPUTS_STORE, "data"))
def plot_residual(regression_inputs):
    model: BivariateEngleGranger = SINGLE_USER_INSTANCE[MODEL]

    inputs = unpack_regression_inputs(regression_inputs)

    residual = model.get_residual(regression_inputs["regression_type"], inputs)

    return px.line(residual)


@callback(Output(IDS.REGRESSION.INPUTS_DIV, "children"), Input(IDS.REGRESSION.TYPE, "value"))
def regression_inputs(regression_type):
    regression = RegressorEnum.enum_from_str(regression_type)

    match regression:
        case RegressorEnum.NAIVE:
            return naive_regressor_inputs()
        case RegressorEnum.ROLLING_WINDOW:
            return rolling_window_regressor_inputs()
        case RegressorEnum.KALMAN_FILTER:
            raise NotImplementedError
        case _:
            raise ValueError(f"RegressorEnum unknown: {regression}")


@callback(
    Output(IDS.REGRESSION.INPUTS_STORE, "data"),
    Input(IDS.REGRESSION.TYPE, "value"),
    Input({"id_type": REGRESSION_INPUT, "name": ALL, "property": ALL}, "value"),
)
def update_regression_store(
    regression_type,
    regression_values,
):
    matched_inputs = {item["id"]["property"]: item["value"] for item in ctx.inputs_list[1]}

    return {"regression_type": regression_type, **matched_inputs}


def unpack_regression_inputs(regression_inputs: dict):
    regression_type = regression_inputs["regression_type"]

    logger.info(f"Unpacking inputs for regresion: {regression_type}")

    match regression_type:
        case RegressorEnum.NAIVE:
            return NaiveRegressorInputs()
        case RegressorEnum.ROLLING_WINDOW:
            return RollingWindowRegressorInputs(
                regression_inputs[IDS.REGRESSION.ID_ROLLING_WINDOW_REGRESSION.WINDOW_LENGTH["property"]],
            )
        case RegressorEnum.KALMAN_FILTER:
            raise NotImplementedError
    raise NotImplementedError
