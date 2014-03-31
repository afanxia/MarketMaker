import datetime
import os, os.path
import pandas as pd

from abc import ABCMeta, abstractmethod

class DataHandler(object):
    """
    DataHandler is an abstract base class providing an interface for
    all subsequent (inherited) data handlers (both live and historic).

    This will replicate how a live strategy would function as current
    market data would be sent "down the pipe". Thus a historic and live
    system will be treated identically by the rest of the backtesting suite.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_latest_quotes(self, symbol, N=1):
        """
        Returns the last N quotes from the symbollist
        """
        raise NotImplementedError("Should implement get_latest_bars()")

    @abstractmethod
    def get_latest_forex(self, symbol, N=1):
        """
        Returns the last N forex datas from the forex_codes list
        """
        raise NotImplementedError("Should implement get_latest_forex()")

    @abstractmethod
    def update_data(self):
        """
        Pushes the latest bar to the latest symbol structure
        for all symbols in the symbol list.
        """
        raise NotImplementedError("Should implement update_bars()")
