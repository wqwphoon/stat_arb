from enum import StrEnum


class StrategyEnum(StrEnum):
    ToyStrategy = "Toy Strategy"
    RollingWindow = "Rolling Window"
    OrnsteinUhlenbeckSDEFit = "Ornstein Uhlenbeck SDE Fit"

    @classmethod
    def enum_from_str(cls, x):
        for enum in cls:
            if enum == x:
                return enum
        raise ValueError(f"StrategyEnum does not exist for string: {x}")
