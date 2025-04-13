import datetime as dt

from dash import dcc, html

from stat_arb.controller import callbacks
from stat_arb.view.ids import IDS


def layout():

    return html.Div(
        [
            dcc.DatePickerRange(
                id=IDS.INPUTS.DATE_RANGE,
                min_date_allowed=dt.date(2000, 1, 1),
                max_date_allowed=dt.date.today() - dt.timedelta(1),
                start_date=dt.date(2023, 1, 1),
                end_date=dt.date(2024, 12, 31),
            ),
            dcc.Dropdown(["^SPX", "AMZN"], id=IDS.INPUTS.TICKER_A),
            dcc.Dropdown(["^SPX", "AMZN"], id=IDS.INPUTS.TICKER_B),
            dcc.Dropdown(
                callbacks.get_datasource_enums(),
                id=IDS.INPUTS.DATA_SOURCE,
                value=callbacks.get_default_datasource_enum(),
            ),
            dcc.Slider(0, 1, 0.1, id=IDS.INPUTS.TEST_TRAIN_SPLIT),
            dcc.Graph(id=IDS.GRAPHS.TICKER_A_PX_SERIES),
        ]
    )
