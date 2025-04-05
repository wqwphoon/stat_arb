import numpy as np
import pytest

from stat_arb.model.statistics.cadf import CointegratedAugmentedDickeyFuller


@pytest.mark.filterwarnings("ignore")
def test_stationarity_for_trending():
    trending = np.arange(100)
    k_vars: int = 1
    result = CointegratedAugmentedDickeyFuller.test_stationarity(trending, k_vars)
    assert not result.significant_at_one_pct()


def test_stationarity_for_cosine():
    x = np.arange(100) * np.pi / 4
    cos_x = np.cos(x)
    result = CointegratedAugmentedDickeyFuller.test_stationarity(cos_x, k_vars=1)
    assert result.significant_at_one_pct()
