from dash import Input, Output, callback

from stat_arb.model.trading_strategy.strategy_enum import StrategyEnum
from stat_arb.view.ids import IDS
from stat_arb.view.trading_strategy_layout import toy_strategy_inputs


def get_strategy_options():
    return [e for e in StrategyEnum]


@callback(Output(IDS.STRATEGY.INPUTS_DIV, "children"), Input(IDS.STRATEGY.TYPE, "value"))
def strategy_inputs(strategy_type):
    strategy = StrategyEnum.enum_from_str(strategy_type)

    if strategy == StrategyEnum.ToyStrategy:
        return toy_strategy_inputs()
    elif strategy == StrategyEnum.RollingWindow:
        raise NotImplementedError
    elif strategy == StrategyEnum.OrnsteinUhlenbeckSDEFit:
        raise NotImplementedError
    else:
        raise ValueError(f"StrategyEnum unknown: {strategy}")
