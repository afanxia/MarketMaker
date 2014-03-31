from Market import Market
from TestingAlgorithms import BuyInTheMorning
from CSVForexTicksHandler import CSVForexTicksHandler
from Broker import Broker
from Portfolio import Portfolio
import logging as log

log.basicConfig(level=log.DEBUG, format=
	"%(asctime)s || %(levelname)s: %(filename)s:%(lineno)d - %(funcName)s: \
	%(message)s")

datahandler = CSVForexTicksHandler(
    '/home/ioan/Dokumente/MarketMaker/marketmaker/histdata/',
    ['EURUSD'])

market = Market('./simulations/', 'test', BuyInTheMorning,
    datahandler, Broker, Portfolio)
market.run(15)
