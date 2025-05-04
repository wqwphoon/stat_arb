import datetime as dt
import logging
from argparse import ArgumentParser, Namespace

from stat_arb.app import main as app_main
from stat_arb.db_run import main as db_main

logger = logging.getLogger(__name__)


def main() -> None:
    parse_args()


def run(args) -> None:
    if args.database:
        logger.info("CLI Database flag detected...")
        db_main()

    else:
        logger.info("Running standard procedure...")
        logger.info("Start Stat Arb app...")
        app_main()


def parse_args() -> None:
    parser = ArgumentParser()

    parser.add_argument("-d", "--database", action="store_true")
    parser.set_defaults(func=run)  # set dot notation for func

    namespace: Namespace = parser.parse_args()
    namespace.func(namespace)
