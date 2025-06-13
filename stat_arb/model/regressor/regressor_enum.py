from enum import StrEnum


class RegressorEnum(StrEnum):
    NAIVE = "Naive"
    ROLLING_WINDOW = "Rolling Window"
    KALMAN_FILTER = "Kalman Filter"  # TODO: Implement

    @classmethod
    def enum_from_str(cls, x):
        for enum in cls:
            if enum == x:
                return enum
        raise ValueError(f"RegressorEnum does not exist for string: {x}")
