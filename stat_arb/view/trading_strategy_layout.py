from dash import dcc, html

from stat_arb.view.ids import IDS


def toy_strategy_inputs():
    return html.Div(
        [
            html.Div(
                [
                    html.P("Enter Threshold:"),
                    html.Div(
                        dcc.Slider(
                            min=0,
                            max=5,
                            step=0.1,
                            id=IDS.STRATEGY.ID_TOY_STRATEGY.ENTER,
                            marks={i / 10: str(i / 10) for i in range(0, 51, 5)},
                            value=1,
                        ),
                        style={"width": "400px"},
                    ),
                ],
                style={"display": "flex", "width": "50%", "marginTop": "20px"},
            ),
            html.Div(
                [
                    html.P("Choose Exit Threshold"),
                    html.Div(
                        dcc.Slider(
                            min=0,
                            max=5,
                            step=0.1,
                            id=IDS.STRATEGY.ID_TOY_STRATEGY.EXIT,
                            marks={i / 10: str(i / 10) for i in range(0, 51, 5)},
                            value=0,
                        ),
                        style={"width": "400px"},
                    ),
                ],
                style={"display": "flex", "width": "50%", "marginTop": "20px"},
            ),
            dcc.Store(id=IDS.STRATEGY.INPUTS_STORE),
        ]
    )


def rolling_window_inputs():
    return html.Div(
        [
            html.Div(
                [
                    html.P("Enter Threshold:"),
                    html.Div(
                        dcc.Slider(
                            min=0,
                            max=5,
                            step=0.1,
                            id=IDS.STRATEGY.ID_ROLLING_WINDOW.ENTER,
                            marks={i / 10: str(i / 10) for i in range(0, 51, 5)},
                            value=1,
                        ),
                        style={"width": "400px"},
                    ),
                ],
                style={"display": "flex", "width": "50%", "marginTop": "20px"},
            ),
            html.Div(
                [
                    html.P("Choose Exit Threshold"),
                    html.Div(
                        dcc.Slider(
                            min=0,
                            max=5,
                            step=0.1,
                            id=IDS.STRATEGY.ID_ROLLING_WINDOW.EXIT,
                            marks={i / 10: str(i / 10) for i in range(0, 51, 5)},
                            value=0,
                        ),
                        style={"width": "400px"},
                    ),
                ],
                style={"display": "flex", "width": "50%", "marginTop": "20px"},
            ),
            html.Div(
                [
                    html.P("Choose Window Length"),
                    html.Div(
                        dcc.Input(
                            type="number",
                            min=1,
                            step=1,
                            value=30,
                            id=IDS.STRATEGY.ID_ROLLING_WINDOW.LENGTH,
                        ),
                        style={"width": "400px"},
                    ),
                ],
                style={"display": "flex", "width": "50%", "marginTop": "20px"},
            ),
            dcc.Store(id=IDS.STRATEGY.INPUTS_STORE),
        ]
    )
