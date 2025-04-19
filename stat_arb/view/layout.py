import datetime as dt

from dash import dcc, html

from stat_arb.controller import callbacks, regression_callbacks
from stat_arb.view.ids import IDS


def layout():

    return html.Div(
        [
            dcc.Dropdown(
                callbacks.get_datasource_enums(),
                id=IDS.INPUTS.DATA_SOURCE,
                value=callbacks.get_default_datasource_enum(),
            ),
            dcc.DatePickerRange(
                id=IDS.INPUTS.DATE_RANGE,
                min_date_allowed=dt.date(2000, 1, 1),
                max_date_allowed=dt.date.today() - dt.timedelta(1),
                start_date=dt.date(2023, 1, 1),
                end_date=dt.date(2024, 12, 31),
            ),
            dcc.Dropdown([], id=IDS.INPUTS.TICKER_A),
            dcc.Dropdown([], id=IDS.INPUTS.TICKER_B),
            dcc.Slider(0, 1, 0.1, id=IDS.INPUTS.TEST_TRAIN_SPLIT),
            dcc.Graph(id=IDS.GRAPHS.PRICE_SERIES),
            dcc.Dropdown(regression_callbacks.get_regressor_options(), id=IDS.REGRESSION.TYPE),
            dcc.Graph(id=IDS.GRAPHS.RESIDUAL),
            html.H4("Cointegrated Augmented Dickey-Fuller Test Result"),
            html.Div(id=IDS.STATISTICS.ADF_RESULT),
            html.H4("Error Correction Model Result"),
            html.Div(id=IDS.STATISTICS.ECM_RESULT),
        ]
    )
