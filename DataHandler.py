import datetime
import os, os.path
import pandas as pd

from abc import ABCMeta, abstractmethod

class DataHandler(object):
    """
    DataHandler is an abstract base class providing an interface for
    all subsequent (inherited) data handlers (both live and historic).

    The abstractmethod functions are function which every DataHandler
    has to implement

    At the moment this parent class doesn't provide any
    functionality, it is here for concept reasons. Also, if later,
    we see that every Broker class needs this or that function,
    we can implement them here.

    """

    __metaclass__ = ABCMeta
