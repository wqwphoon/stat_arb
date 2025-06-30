from dash import dcc, html

from stat_arb.view.ids import IDS


def toy_strategy_inputs():
    return html.Div(
        [
            html.Div(
                [
                    html.Label("Enter Threshold: "),
                    dcc.Input(type="number", value=1, step=0.01, id=IDS.STRATEGY.ID_TOY_STRATEGY.ENTER),
                ],
                style={"marginTop": "20px"},
            ),
            html.Div(
                [
                    html.Label("Exit Threshold: "),
                    dcc.Input(type="number", value=0, step=0.05, id=IDS.STRATEGY.ID_TOY_STRATEGY.EXIT),
                ],
                style={"marginTop": "10px"},
            ),
            dcc.Store(id=IDS.STRATEGY.INPUTS_STORE),
        ]
    )


def rolling_window_inputs():
    return html.Div(
        [
            html.Div(
                [
                    html.Label("Enter Threshold: "),
                    dcc.Input(type="number", value=1, step=0.01, id=IDS.STRATEGY.ID_ROLLING_WINDOW.ENTER),
                ],
                style={"marginTop": "20px"},
            ),
            html.Div(
                [
                    html.Label("Exit Threshold: "),
                    dcc.Input(type="number", value=0, step=0.05, id=IDS.STRATEGY.ID_ROLLING_WINDOW.EXIT),
                ],
                style={"marginTop": "10px"},
            ),
            html.Div(
                [
                    html.Label("Window Length: "),
                    dcc.Input(
                        type="number", min=1, step=1, value=252, id=IDS.STRATEGY.ID_ROLLING_WINDOW.LENGTH
                    ),
                ],
                style={"marginTop": "10px"},
            ),
            dcc.Store(id=IDS.STRATEGY.INPUTS_STORE),
        ]
    )
