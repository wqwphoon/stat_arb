from enum import Enum


class DataHandlerEnum(Enum):
    YAHOO = "Yahoo"
    SIMULATED = "Simulated"


def get_enum_from_str(x: str) -> DataHandlerEnum:
    for enum in DataHandlerEnum:
        if enum.value == x:
            return enum
    raise ValueError(f"Provided string {x} does not have an associated enum")
