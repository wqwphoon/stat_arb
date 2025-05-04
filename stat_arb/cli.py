import logging
from argparse import ArgumentParser, Namespace

from stat_arb.app import main as app_main
from stat_arb.db_run import main as db_main
from stat_arb.model.local_store.ticker_snapshot.ticker_snapshot import main as ticker_main

logger = logging.getLogger(__name__)


def main() -> None:
    parse_args()


def run(args: Namespace) -> None:
    if args.database:
        logger.info("CLI Database flag detected...")
        db_main()
    elif args.ticker:
        logger.info("CLI Ticker flag detected...")
        ticker_main()
    else:
        logger.info("Running standard procedure...")
        logger.info("Start Stat Arb app...")
        app_main()


def parse_args() -> None:
    parser = ArgumentParser(
        description="Pairs Trading Dashboard", epilog="Execute with no arguments for Pairs Trading Dashboard"
    )

    parser.add_argument("-d", "--database", action="store_true", help="Create ticker prices local database")
    parser.add_argument("-t", "--ticker", action="store_true", help="Create updated S&P500 ticker list")
    parser.set_defaults(func=run)  # set dot notation for func

    namespace: Namespace = parser.parse_args()
    namespace.func(namespace)
