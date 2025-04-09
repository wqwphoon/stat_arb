import datetime as dt
import logging

import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, callback, dash_table, dcc, html

from stat_arb.model.bivariate_engle_granger import BivariateEngleGranger
from stat_arb.model.data import DataHandlerEnum

logger = logging.getLogger("stat_arb")


def app_main():
    logger.info("Configuring Dash instance...")

    app = Dash()

    app.layout = html.Div(
        [
            dcc.DatePickerRange(
                id="date-picker-range",
                min_date_allowed=dt.date(2000, 1, 1),
                max_date_allowed=dt.date.today() - dt.timedelta(1),
            ),
            dcc.Dropdown(["^SPX", "AMZN"], id="ticker-a"),
            dcc.Dropdown(["^SPX", "AMZN"], id="ticker-b"),
            html.Div(id="test"),
        ]
    )

    @callback(
        Output(component_id="test", component_property="children"),
        Input(component_id="ticker-a", component_property="value"),
    )
    def update_test(value):
        return f"selected {value}"

    # df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv")

    # app.layout = [
    #     html.Div(children="My First App with Data"),
    #     html.Hr(),
    #     dcc.RadioItems(
    #         options=["pop", "lifeExp", "gdpPercap"], value="lifeExp", id="controls-and-radio-item"
    #     ),
    #     dash_table.DataTable(data=df.to_dict("records"), page_size=6),
    #     dcc.Graph(figure={}, id="controls-and-graph"),
    # ]

    # @callback(
    #     Output(component_id="controls-and-graph", component_property="figure"),
    #     Input(component_id="controls-and-radio-item", component_property="value"),
    # )
    # def update_graph(col_chosen):
    #     fig = px.histogram(df, x="continent", y=col_chosen, histfunc="avg")
    #     return fig

    app.run(debug=True)

    # ticker_a = "MA"
    # ticker_b = "V"
    # start = dt.datetime(2020, 1, 1)
    # end = dt.datetime(2025, 1, 8)
    # live = dt.datetime(2025, 1, 6)
    # data_enum = DataHandlerEnum.SIMULATED
    # model = BivariateEngleGranger(ticker_a, ticker_b, start, end, live, data_enum)
    # model.run()

    pass
