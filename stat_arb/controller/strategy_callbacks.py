from logging import getLogger

import plotly
import plotly.express as px
import plotly.subplots
from dash import ALL, Input, Output, callback, ctx, html

from stat_arb.controller.callbacks import MODEL, SINGLE_USER_INSTANCE
from stat_arb.model.bivariate_engle_granger import BivariateEngleGranger
from stat_arb.model.trading_strategy import RollingWindowInputs, StrategyEnum, ToyStrategyInputs
from stat_arb.view.ids import IDS, STRATEGY_INPUT
from stat_arb.view.trading_strategy_layout import rolling_window_inputs, toy_strategy_inputs

logger = getLogger(__name__)


def get_strategy_options():
    return [e for e in StrategyEnum]


@callback(Output(IDS.STRATEGY.INPUTS_DIV, "children"), Input(IDS.STRATEGY.TYPE, "value"))
def strategy_inputs(strategy_type):
    strategy = StrategyEnum.enum_from_str(strategy_type)

    if strategy == StrategyEnum.ToyStrategy:
        return toy_strategy_inputs()
    elif strategy == StrategyEnum.RollingWindow:
        return rolling_window_inputs()
    elif strategy == StrategyEnum.OrnsteinUhlenbeckSDEFit:
        raise NotImplementedError
    else:
        raise ValueError(f"StrategyEnum unknown: {strategy}")


@callback(
    Output(IDS.STRATEGY.INPUTS_STORE, "data"),
    Input(IDS.STRATEGY.TYPE, "value"),
    Input({"id_type": STRATEGY_INPUT, "name": ALL, "property": ALL}, "value"),
)
def update_strategy_store(
    strategy_type,
    strategy_values,
):
    logger.info(ctx.inputs_list[1])
    matched_inputs = {item["id"]["property"]: item["value"] for item in ctx.inputs_list[1]}

    logger.info(f"{matched_inputs=}")

    return {"strategy_type": strategy_type, **matched_inputs}


@callback(Output(IDS.STRATEGY.OUTPUT_DIV, "children"), Input(IDS.STRATEGY.INPUTS_STORE, "data"))
def strategy_output_div(store):
    model: BivariateEngleGranger = SINGLE_USER_INSTANCE[MODEL]

    logger.info(f"strategy_output_div - {store}")

    return html.Div(
        [
            html.P(f"Chosen Strategy: {store["strategy_type"]}"),
            html.P(f"Enter Threshold: {store["enter"]}"),
            html.P(f"Exit Threshold: {store["exit"]}"),
            html.P(f"Cumulative Return: {model.backtest_results.get_cum_return():.4f}"),
        ]
    )


@callback(Output(IDS.STRATEGY.OUTPUT_PLOT, "figure"), Input(IDS.STRATEGY.INPUTS_STORE, "data"))
def plot_strategy_backtest(strategy_inputs):
    model: BivariateEngleGranger = SINGLE_USER_INSTANCE[MODEL]

    inputs = unpack_strategy_inputs(strategy_inputs)

    trading_strategy_results = model.backtest(strategy_inputs["strategy_type"], inputs)

    df = trading_strategy_results.get_backtest()

    fig = plotly.subplots.make_subplots(specs=[[{"secondary_y": True}]])

    fig1 = px.line(df, y=["Z-Score", "Signal"], title="Signal / Z-Score (Primary Y)")
    # fig2 = px.line(df, y=["Residual"], title="Residual (Secondary Y)")

    fig.add_traces(fig1.data)

    # for trace in fig2.data:
    #     trace.showlegend = True
    #     fig.add_traces(trace, secondary_ys=[True])

    fig.update_layout(title_text="Trading Strategy", height=800)

    return fig


def unpack_strategy_inputs(strategy_inputs: dict):
    strategy_type = strategy_inputs["strategy_type"]

    logger.info(f"Unpacking inputs for strategy: {strategy_type}")

    match strategy_type:
        case StrategyEnum.ToyStrategy:
            return ToyStrategyInputs(
                strategy_inputs[IDS.STRATEGY.ID_TOY_STRATEGY.ENTER["property"]],
                strategy_inputs[IDS.STRATEGY.ID_TOY_STRATEGY.EXIT["property"]],
            )
        case StrategyEnum.RollingWindow:
            return RollingWindowInputs(
                strategy_inputs[IDS.STRATEGY.ID_ROLLING_WINDOW.ENTER["property"]],
                strategy_inputs[IDS.STRATEGY.ID_ROLLING_WINDOW.EXIT["property"]],
                strategy_inputs[IDS.STRATEGY.ID_ROLLING_WINDOW.LENGTH["property"]],
            )
        case StrategyEnum.OrnsteinUhlenbeckSDEFit:
            raise NotImplementedError
    raise NotImplementedError
