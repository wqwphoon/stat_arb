from abc import ABC, abstractmethod


class TradingStrategy(ABC):
    @abstractmethod
    def read_input(self):
        pass

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def get_output(self):
        pass
