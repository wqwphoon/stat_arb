from abc import ABC, abstractmethod

import pandas as pd


class DataHandler(ABC):
    """Interface to define DataHandler contract."""

    @abstractmethod
    def get_close_prices(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_normalised_close_prices(self) -> pd.DataFrame:
        pass
