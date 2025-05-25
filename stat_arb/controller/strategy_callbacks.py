from dash import Input, Output, callback

from stat_arb.model.trading_strategy.strategy_enum import StrategyEnum
from stat_arb.view.ids import IDS


def get_strategy_options():
    return [e for e in StrategyEnum]
