from abc import ABC, abstractmethod


class DataHandler(ABC):
    """Interface to define DataHandler contract."""

    @abstractmethod
    def get_close_prices(self):
        pass

    @abstractmethod
    def get_normalised_close_prices(self):
        pass
