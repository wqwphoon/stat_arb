import datetime as dt

import dash_bootstrap_components as dbc
from dash import dcc, html

from stat_arb.controller import callbacks, regression_callbacks
from stat_arb.view.ids import IDS


def layout():

    return html.Div(
        [
            html.H1("Pairs Trading Dashboard", style={"marginTop": "20px"}),
            html.Div(
                [
                    html.H3("Step 1: Select Data Source"),
                    dcc.Dropdown(
                        callbacks.get_datasource_enums(),
                        id=IDS.STORE_INPUTS.DATA_SOURCE,
                        value=callbacks.get_default_datasource_enum(),
                        style={"width": "40%"},
                    ),
                ]
            ),
            html.Div(
                [
                    html.H3("Step 2: Select Stock Data"),
                    html.Div(
                        [
                            html.Div(
                                [
                                    dcc.Dropdown(
                                        [],
                                        id=IDS.STORE_INPUTS.TICKER_A,
                                        placeholder="Stock A (e.g., AAPL)",
                                    )
                                ],
                                style={"width": "20%", "display": "inline-block"},
                            ),
                            html.Div(
                                [
                                    dcc.Dropdown(
                                        [],
                                        id=IDS.STORE_INPUTS.TICKER_B,
                                        placeholder="Stock B (e.g., MSFT)",
                                    )
                                ],
                                style={"width": "20%", "display": "inline-block"},
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.P(
                                "Choose the start and end dates.",
                            ),
                            dcc.DatePickerRange(
                                id=IDS.STORE_INPUTS.DATE_RANGE,
                                min_date_allowed=dt.date(2000, 1, 1),
                                max_date_allowed=dt.date.today() - dt.timedelta(1),
                                start_date=dt.date(2023, 1, 1),
                                end_date=dt.date(2024, 12, 31),
                            ),
                        ],
                        style={"marginTop": "10px"},
                    ),
                    html.Button("Load Data", id=IDS.INPUTS.DATA_INPUT, style={"marginTop": "20px"}),
                ]
            ),
            dcc.Loading(
                children=[
                    dcc.Graph(
                        id=IDS.GRAPHS.PRICE_SERIES,
                        config={"responsive": True},
                        style={"height": "100%", "width": "100%"},
                    )
                ]
            ),
            dcc.Slider(0, 1, 0.1, id=IDS.STORE_INPUTS.TEST_TRAIN_SPLIT),
            # dcc.Graph(id=IDS.GRAPHS.PRICE_SERIES),
            html.Div(
                [
                    html.H3("Step 3: Select Regression Method"),
                    dcc.RadioItems(regression_callbacks.get_regressor_options(), id=IDS.REGRESSION.TYPE),
                    dcc.Graph(id=IDS.GRAPHS.RESIDUAL),
                ]
            ),
            html.Div(
                [
                    html.H3("Step 4: Review Statistical Tests"),
                    dbc.Toast(
                        [
                            html.Div(id=IDS.STATISTICS.ADF_RESULT),
                        ],
                        header="Cointegrated Augmented Dickey-Fuller Test Result",
                        is_open=True,
                    ),
                    dbc.Toast(
                        [
                            html.Div(id=IDS.STATISTICS.ECM_RESULT),
                        ],
                        header="Error Correction Model Result",
                        is_open=True,
                    ),
                ]
            ),
        ],
        style={"paddingLeft": "40px"},
    )
