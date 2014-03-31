from Market import Market
from TestingAlgorithm import TestingAlgorithm
from LiteForexHandler import LiteForexHandler
from Broker import Broker
from Portfolio import Portfolio



market = Market('./simulations/', 'test', TestingAlgortihm, LiteForexHandler,
    Broker, Portfolio)
market.run()
