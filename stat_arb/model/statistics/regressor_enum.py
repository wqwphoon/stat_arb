from enum import StrEnum


class RegressorEnum(StrEnum):
    NAIVE = "Naive"
    ROLLING_WINDOW = "Rolling Window"
    KALMAN_FILTER = "Kalman Filter"  # TODO: Implement
