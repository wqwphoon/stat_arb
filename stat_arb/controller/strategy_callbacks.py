from logging import getLogger

import plotly.express as px
from dash import Input, Output, callback

from stat_arb.controller.callbacks import MODEL, SINGLE_USER_INSTANCE
from stat_arb.model.bivariate_engle_granger import BivariateEngleGranger
from stat_arb.model.trading_strategy.strategy_enum import StrategyEnum
from stat_arb.model.trading_strategy.toy_strategy import ToyStrategyInputs
from stat_arb.view.ids import IDS
from stat_arb.view.trading_strategy_layout import toy_strategy_inputs

logger = getLogger(__name__)


def get_strategy_options():
    return [e for e in StrategyEnum]


@callback(Output(IDS.STRATEGY.INPUTS_DIV, "children"), Input(IDS.STRATEGY.TYPE, "value"))
def strategy_inputs(strategy_type):
    strategy = StrategyEnum.enum_from_str(strategy_type)

    if strategy == StrategyEnum.ToyStrategy:
        return toy_strategy_inputs()
    elif strategy == StrategyEnum.RollingWindow:
        raise NotImplementedError
    elif strategy == StrategyEnum.OrnsteinUhlenbeckSDEFit:
        raise NotImplementedError
    else:
        raise ValueError(f"StrategyEnum unknown: {strategy}")


@callback(
    Output(IDS.STRATEGY.INPUTS_STORE, "data"),
    Input(IDS.STRATEGY.TYPE, "value"),
    Input(IDS.STRATEGY.ID_TOY_STRATEGY.ENTER, "value"),
    Input(IDS.STRATEGY.ID_TOY_STRATEGY.EXIT, "value"),
)
def update_strategy_store(strategy_type, toy_strategy_enter, toy_strategy_exit):
    return {
        "strategy_type": strategy_type,
        "toy_strategy_enter": toy_strategy_enter,
        "toy_strategy_exit": toy_strategy_exit,
    }


@callback(Output(IDS.STRATEGY.OUTPUT_PLOT, "figure"), Input(IDS.STRATEGY.INPUTS_STORE, "data"))
def plot_strategy_backtest(strategy_inputs):
    model: BivariateEngleGranger = SINGLE_USER_INSTANCE[MODEL]

    inputs = unpack_strategy_inputs(strategy_inputs)

    df = model.backtest(strategy_inputs["strategy_type"], inputs)

    return px.line(df)


def unpack_strategy_inputs(strategy_inputs: dict):
    strategy_type = strategy_inputs["strategy_type"]

    logger.info(f"Unpacking inputs for strategy: {strategy_type}")

    match strategy_type:
        case StrategyEnum.ToyStrategy:
            return ToyStrategyInputs(
                strategy_inputs["toy_strategy_enter"], strategy_inputs["toy_strategy_exit"]
            )
        case StrategyEnum.RollingWindow:
            raise NotImplementedError
        case StrategyEnum.OrnsteinUhlenbeckSDEFit:
            raise NotImplementedError
    raise NotImplementedError
