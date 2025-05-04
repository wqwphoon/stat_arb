import logging
from argparse import ArgumentParser, Namespace

from stat_arb.run import main as _main

logger = logging.getLogger(__name__)


def main() -> None:

    # Parse command line arguments
    parse_args()


def run(args) -> None:
    print(args)
    print(args.database)
    logger.info("test")

    _main()


def parse_args() -> None:
    parser = ArgumentParser()

    parser.add_argument("-d", "--database", action="store_true")
    parser.add_argument("-n", "--number", type=int)
    parser.set_defaults(func=run)  # set dot notation for func

    namespace: Namespace = parser.parse_args()
    namespace.func(namespace)
