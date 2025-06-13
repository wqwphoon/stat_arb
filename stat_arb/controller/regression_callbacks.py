import plotly.express as px
from dash import Input, Output, callback

from stat_arb.controller.callbacks import MODEL, SINGLE_USER_INSTANCE
from stat_arb.model.bivariate_engle_granger import BivariateEngleGranger
from stat_arb.model.regressor import RegressorEnum
from stat_arb.view.ids import IDS
from stat_arb.view.regressor_layout import naive_regressor_inputs, rolling_window_regressor_inputs


def get_regressor_options():
    return [e for e in RegressorEnum]


@callback(Output(IDS.GRAPHS.RESIDUAL, "figure"), Input(IDS.REGRESSION.TYPE, "value"))
def plot_residual(regression_type):
    model: BivariateEngleGranger = SINGLE_USER_INSTANCE[MODEL]
    return px.line(model.get_residual())


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
