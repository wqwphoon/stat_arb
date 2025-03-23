import datetime as dt

from stat_arb.model.data_handler import DataHandler


class BivariateEngleGranger:
    def __init__(
        self,
        ticker_a: str,
        ticker_b: str,
        start_date: dt.datetime,
        end_date: dt.datetime,
        live_start_date: dt.datetime,
    ):
        self.ticker_a = ticker_a
        self.ticker_b = ticker_b
        self.start_date = start_date
        self.end_date = end_date
        self.live_start_date = live_start_date

    def run(self):
        data = DataHandler([self.ticker_a, self.ticker_b], self.start_date, self.end_date)

        data.get_close_prices()

        pass


if __name__ == "__main__":
    ticker_a = "MA"
    ticker_b = "V"
    start = dt.datetime(2025, 1, 1)
    end = dt.datetime(2025, 1, 8)
    live = dt.datetime(2025, 1, 6)
    model = BivariateEngleGranger(ticker_a, ticker_b, start, end, live)
    model.run()
    pass
