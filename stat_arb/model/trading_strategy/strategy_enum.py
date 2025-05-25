from enum import StrEnum


class StrategyEnum(StrEnum):
    ToyStrategy = "Toy Strategy"
    RollingWindow = "Rolling Window"
    OrnsteinUhlenbeckSDEFit = "Ornstein Uhlenbeck SDE Fit"
