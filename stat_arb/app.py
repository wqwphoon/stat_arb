import logging

import dash_bootstrap_components as dbc
from dash import Dash

from stat_arb.view.layout import layout

logger = logging.getLogger(__name__)


def main():
    logger.info("Configuring Dash instance...")

    app = Dash(__name__, external_stylesheets=[dbc.themes.ZEPHYR])

    app.layout = layout()

    app.run(debug=True)
    # app.run()

    pass
