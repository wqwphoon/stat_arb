from enum import Enum


class DataHandlerEnum(Enum):
    YAHOO = "Yahoo"
    SIMULATED = "Simulated"


if __name__ == "__main__":
    var = DataHandlerEnum.Yahoo
