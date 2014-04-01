from abc import ABCMeta, abstractmethod

class Broker(object):
    """
        Broker class to extended by every object which is used as a
        Broker. At the moment Tick Data is used, so the TickBroker is
        enough. In future, when we have to use other (prbly less
        precise) data kinds (e.g. bars), brokers have to be implemented
        to deal with this data kinds. For functionality the broker
        classes provide, look at them directly.

        At the moment this parent class doesn't provide any
        functionality, it is here for concept reasons. Also, if later,
        we see that every Broker class needs this or that function,
        we can implement them here.
    """

    __metaclass__ = ABCMeta
