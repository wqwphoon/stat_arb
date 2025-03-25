from abc import ABC, abstractmethod


class DataHandler(ABC):
    @abstractmethod
    def get_close_prices(self):
        pass
