from enum import StrEnum


class StrategyEnum(StrEnum):
    ToyStrategy = "Toy Strategy"
    RollingWindow = "Rolling Window"
    OrnsteinUhlenbeckSDEFit = "Ornstein Uhlenbeck SDE Fit"

    def enum_from_str(x):
        for enum in StrategyEnum:
            if enum == x:
                return enum
        raise ValueError(f"StrategyEnum does not exist for string: {x}")
