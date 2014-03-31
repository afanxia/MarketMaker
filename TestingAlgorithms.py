from TradingAlgorithm import TradingAlgorithm
from datetime import datetime, time
import logging as log

class TestingAlgorithm(TradingAlgorithm):

	def __init__(self, market, broker, portfolio):
		log.debug("Initiating TestingAlgorithm Object")
		self.market = market
		self.broker = broker
		self.portfolio = portfolio
		self.market.data.time_change.registerObserver(self.say_hi)

	def say_hi(self, notImportantForMe):
		log.info("Hi guys, I heard we have new Data, i'll sleep: It is "
		"%s a clock" % self.market.data.get_current_time())


class BuyInTheMorning(TradingAlgorithm):
	"""A Testing algorithm which buys US Dollars in the Morning and
		sells them in the evening. Not serious strategy. Used for
		testing market orders
	"""

	def __init__(self, market, broker, portfolio):
		log.debug("Initiating TestingAlgorithm Object")
		self.market = market
		self.broker = broker
		self.portfolio = portfolio
		self.market.data.time_change.registerObserver(self.time_changed)
		self.broker.order_fill.registerObserver(
			self.order_filled)

		self.bought_today = False
		self.name = 'BuyInTheMorning'


	def time_changed(self, DataHandler):
		if (self.bought_today == False and
			time(6) < self.market.data.get_current_time().time() <
			time(7)):
			self.bought_today = True
			order = {'trader_id':self.name, 'amount': 10000,
				'fxcode':'EURUSD', 'kind': 'buy', 'type': 'market'}
			self.broker.order_xchange(order, self.portfolio)
		elif (self.bought_today == True and
			time(18) < self.market.data.get_current_time().time() <
			time(19)):
			self.bought_today = False
			order = {'trader_id':self.name, 'amount': 0,
				'fxcode':'EURUSD', 'kind': 'sell', 'type': 'market'}
			self.broker.order_xchange(order, self.portfolio)

	def order_filled(self, order):
		if order['trader_id'] == self.name:
			log.info("One of my orders got filled")
			print(order)
			print(self.portfolio.get_portfolio())
			
		
