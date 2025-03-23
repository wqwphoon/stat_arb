import pandas as pd


class BivariateEngleGranger:
    def __init__(
        self,
        ticker_a: str,
        ticker_b: str,
        start_date: pd.DateTime,
        end_date: pd.DateTime,
        live_start_date: pd.DateTime,
    ):
        self.ticker_a = ticker_a
        self.ticker_b = ticker_b
        self.start_date = start_date
        self.end_date = end_date
        self.live_start_date = live_start_date

    def run(self):
        pass
