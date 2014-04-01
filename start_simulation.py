from Market import Market
from TestingAlgorithms import BuyInTheMorning
from CSVForexTicksHandler import CSVForexTicksHandler
from TickBroker import TickBroker
from Portfolio import Portfolio
import logging as log

log.basicConfig(level=log.DEBUG, format=
	"%(asctime)s || %(levelname)s: %(filename)s:%(lineno)d - %(funcName)s: \
	%(message)s")

datahandler = CSVForexTicksHandler(
    '/home/ioan/Dokumente/MarketMaker/marketmaker/histdata/',
    ['EURUSD'])

market = Market(BuyInTheMorning, datahandler, TickBroker, Portfolio, 'test')
market.run(30)
