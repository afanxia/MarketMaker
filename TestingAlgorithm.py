from TradingAlgorithm import TradingAlgorithm

class TestingAlgorithm(TradingAlgorithm):

	def __init__(self, market, broker, portfolio):
		self.market = market
		self.broker = broker
		self.portfolio = portfolio
		self.market.change.registerObserver(self.say_hi)

	def say_hi(data):
		print("Hi guys, I heard we have new Data, i'll sleep:")
		print(data)
		sleep(10)
