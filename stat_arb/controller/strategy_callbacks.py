from logging import getLogger

import pandas as pd
import plotly
import plotly.express as px
import plotly.subplots
from dash import ALL, Input, Output, callback, ctx, dash_table, html

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
    matched_inputs = {item["id"]["property"]: item["value"] for item in ctx.inputs_list[1]}

    return {"strategy_type": strategy_type, **matched_inputs}


@callback(Output(IDS.STRATEGY.OUTPUT_DIV, "children"), Input(IDS.STRATEGY.OUTPUT_BACKTEST_PLOT, "figure"))
def strategy_output_div(_):
    model: BivariateEngleGranger = SINGLE_USER_INSTANCE[MODEL]

    results = model.backtest_results
    data_dict = {
        "Sharpe Ratio": f"{results.get_sharpe_ratio():.2f}",
        "Sortino Ratio": f"{results.get_sortino_ratio():.2f}",
        "Annualised Return": f"{results.get_annualised_return():.2%}",
        "Annualised Volatility": f"{results.get_annualised_vol():.2%}",
        "Maximum Drawdown": f"{results.get_max_drawdown():.2%}",
    }

    table_data = [{"Metric": k, "Value": v} for k, v in data_dict.items()]

    return html.Div(
        dash_table.DataTable(
            table_data,
            [{"name": "Metric", "id": "Metric"}, {"name": "Value", "id": "Value"}],
            style_table={"width": "50%"},
        )
    )

    # return html.Div(
    #     [
    #         html.P(f"Chosen Strategy: {store["strategy_type"]}"),
    #         html.P(f"Enter Threshold: {store["enter"]}"),
    #         html.P(f"Exit Threshold: {store["exit"]}"),
    #         html.P(f"Cumulative Return: {model.backtest_results.get_cum_return():.4f}"),
    #     ]
    # )


@callback(Output(IDS.STRATEGY.OUTPUT_BACKTEST_PLOT, "figure"), Input(IDS.STRATEGY.INPUTS_STORE, "data"))
def plot_strategy_backtest(strategy_inputs):
    model: BivariateEngleGranger = SINGLE_USER_INSTANCE[MODEL]

    inputs = unpack_strategy_inputs(strategy_inputs)

    trading_strategy_results = model.backtest(strategy_inputs["strategy_type"], inputs)

    df = trading_strategy_results.get_backtest()

    fig = plotly.subplots.make_subplots(rows=2, cols=1, subplot_titles=("Backtest", "Cumulative Return"))

    fig1 = px.line(df, y=["Residual"], title="Residual")

    shapes = []
    dates = df.index
    for i, signal in enumerate(df["Signal"]):

        if i != len(df) - 1:
            colour = None
            if signal == 1:
                colour = "green"
            elif signal == -1:
                colour = "red"

            shapes.append(
                {
                    "type": "rect",
                    "xref": "x",
                    "yref": "y1",
                    "x0": dates[i],
                    "y0": -abs(2 * df["Residual"].min()),
                    "x1": dates[i + 1],
                    "y1": abs(2 * df["Residual"].max()),
                    "fillcolor": colour,
                    "opacity": 0.2,
                    "line_width": 0,
                }
            )

    fig1.update_layout(title_text="Trading Strategy", height=800, shapes=shapes)

    fig2 = px.line(df, y=["Cumulative_return"], title="Cumulative Return")

    for trace in fig1.data:
        fig.add_traces(trace, rows=1, cols=1)

    for trace in fig2.data:
        trace.showlegend = False
        fig.add_traces(trace, rows=2, cols=1)

    fig.update_layout(title_text="Trading Strategy Plots", height=800, shapes=shapes)

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
