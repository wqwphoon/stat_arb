import datetime as dt

from dash import dcc, html

from .ids import IDS


def layout():
    return html.Div(
        [
            dcc.DatePickerRange(
                id=IDS.INPUTS.DATE_RANGE,
                min_date_allowed=dt.date(2000, 1, 1),
                max_date_allowed=dt.date.today() - dt.timedelta(1),
            ),
            dcc.Dropdown(["^SPX", "AMZN"], id=IDS.INPUTS.TICKER_A),
            dcc.Dropdown(["^SPX", "AMZN"], id=IDS.INPUTS.TICKER_B),
            dcc.Dropdown(["Yahoo Finance", "Simulated"], id=IDS.INPUTS.DATA_SOURCE),
            dcc.Slider(0, 1, 0.1, id=IDS.INPUTS.TEST_TRAIN_SPLIT),
        ]
    )
