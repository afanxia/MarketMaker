from TradingAlgorithm import TradingAlgorithm
import logging as log

class TestingAlgorithm(TradingAlgorithm):

	def __init__(self, market, broker, portfolio):
		log.debug("Initation TestingAlgorithm Object")
		self.market = market
		self.broker = broker
		self.portfolio = portfolio
		self.market.data.time_change.registerObserver(self.say_hi)

	def say_hi(self, mata):
		log.info("Hi guys, I heard we have new Data, i'll sleep: It is "
		"%s a clock" % self.market.data.get_current_time())
		print(mata)
