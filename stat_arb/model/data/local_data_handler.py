import pandas as pd
import yfinance as yf

from stat_arb.model.data.data_handler import BaseDataHandler


class LocalDataHandler(BaseDataHandler):
    def get_close_prices(self):
        pass

    def get_normalised_close_prices(self):
        pass
