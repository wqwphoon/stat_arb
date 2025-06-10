from dash import dcc, html

from stat_arb.view.ids import IDS


def naive_regressor_inputs():
    return None


def rolling_window_regressor_inputs():
    return html.Div(
        [
            html.Div(
                [
                    html.P("Choose Window Length"),
                    html.Div(
                        dcc.Input(
                            type="number",
                            min=1,
                            step=1,
                            value=30,
                            id=IDS.REGRESSION.ID_ROLLING_WINDOW_REGRESSION.WINDOW_LENGTH,
                        ),
                        style={"width": "400px"},
                    ),
                ],
                style={"display": "flex", "width": "50%", "marginTop": "20px"},
            ),
            # dcc.Store(id=IDS.STRATEGY.INPUTS_STORE),
        ]
    )
