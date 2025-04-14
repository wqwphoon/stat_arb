import logging

import plotly.express as px
from dash import Input, Output, callback, exceptions

from stat_arb.controller.callbacks import MODEL, SINGLE_USER_INSTANCE
from stat_arb.model.bivariate_engle_granger import BivariateEngleGranger
from stat_arb.model.data.data_handler_enum import DataHandlerEnum, get_enum_from_str
from stat_arb.model.statistics.regressor_enum import RegressorEnum
from stat_arb.view.ids import IDS


def get_regressor_options():
    return [e for e in RegressorEnum]


@callback(Output(IDS.GRAPHS.RESIDUAL, "figure"), Input(IDS.REGRESSION.TYPE, "value"))
def plot_residual(regression_type):
    model: BivariateEngleGranger = SINGLE_USER_INSTANCE[MODEL]
    return px.line(model.get_residual())
