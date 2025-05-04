import logging

from dash import Dash

from stat_arb.view.layout import layout

logger = logging.getLogger(__name__)


def app_main():
    logger.info("Configuring Dash instance...")

    app = Dash()

    app.layout = layout()

    app.run(debug=True)

    pass
