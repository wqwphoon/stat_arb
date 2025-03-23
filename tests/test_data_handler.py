import pytest

from stat_arb.model.data_handler import DataHandler


def test_empty_ticker_list():
    with pytest.raises(ValueError):
        data = DataHandler([], "2025-01-01", "2025-01-08")
        data.get_close_prices()
