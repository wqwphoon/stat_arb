from enum import StrEnum


class DataHandlerEnum(StrEnum):
    YAHOO = "Yahoo"
    SIMULATED = "Simulated"
    LOCAL = "Local"


def get_enum_from_str(x: str) -> DataHandlerEnum:
    for enum in DataHandlerEnum:
        if enum.value == x:
            return enum
    raise ValueError(f"Provided string {x} does not have an associated enum")
