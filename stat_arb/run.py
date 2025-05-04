import argparse
import logging

from stat_arb.app import app_main

logger = logging.getLogger(__name__)


def main():
    logger.info("Start Stat Arb app...")

    app_main()


if __name__ == "__main__":
    main()
