from TradingAlgorithm import TradingAlgorithm
from datetime import datetime, time, timedelta
import logging as log
from CSVForexTicksHandler import DataNotAvailable
import numpy

class TwoAverages(TradingAlgorithm):

	def __init__(self, market, broker, portfolio):
		log.debug("Initiating TestingAlgorithm Object")
		self.market = market
		self.broker = broker
		self.portfolio = portfolio
		self.market.data.time_change.registerObserver(self.time_changed)
		#self.broker.order_fill.registerObserver(self.order_filled)
		self.market.game_end.registerObserver(self.game_ends)

		self.bought_today = False
		self.my_orders = []

		self.avg_differ = []


		#CONFIGURATION
		#shorta, longa -> last n seconds the short and long average will be taken of
		self.shorta = 8
		self.longa = 60
		#how much do the averages have to differ to make a buy/sell signal
		self.avg_min_differ = 0.000025

	def time_changed(self, data):
		try:
			latest_data = self.market.data.get_latest_data(
				'EURUSD', timedelta(seconds=self.longa))
		except DataNotAvailable:
			return
		rates = (latest_data['ask'] + latest_data['bid'])/2
		newer_rates = rates[self.market.data.get_current_time()
			- timedelta(seconds=self.shorta):]
		long_average = rates.mean()
		short_average = newer_rates.mean()
		if (not numpy.isnan(short_average) and
			not numpy.isnan(long_average)):
			self.avg_differ.append(abs( short_average - long_average))

			if short_average - long_average > self.avg_min_differ:
				order = {'amount': 10000, 'fxcode':'EURUSD',
					'kind': 'buy', 'type': 'market'}
				order_id = self.broker.order_xchange(order,
					self.portfolio)
				self.my_orders.append(order_id)
			elif long_average - short_average > self.avg_min_differ:
				order = {'amount': 10000, 'fxcode':'EURUSD',
					'kind': 'sell', 'type': 'market'}
				order_id = self.broker.order_xchange(order,
					self.portfolio)
				self.my_orders.append(order_id)

	def order_filled(self, order):
		if order['id'] in self.my_orders:
			print(self.portfolio.get_portfolio())
			self.my_orders.remove(order['id'])

	def game_ends(self):
		print("Averages differ %f in average" %
			numpy.mean(self.avg_differ))

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
		self.my_orders = []


	def time_changed(self, DataHandler):
		if (self.bought_today == False and
			time(6) < self.market.data.get_current_time().time() <
			time(7)):
			self.bought_today = True
			order = {'amount': 10000, 'fxcode':'EURUSD', 'kind': 'sell', 
				'type': 'market'}
			order_id = self.broker.order_xchange(order, self.portfolio)
			self.my_orders.append(order_id)
		elif (self.bought_today == True and
			time(18) < self.market.data.get_current_time().time() <
			time(19)):
			self.bought_today = False
			order = {'amount': 0, 'fxcode':'EURUSD', 'kind': 'buy', 
				'type': 'market'}
			order_id = self.broker.order_xchange(order, self.portfolio)
			self.my_orders.append(order_id)

	def order_filled(self, order):
		if order['id'] in self.my_orders:
			print(self.portfolio.get_portfolio())
			self.my_orders.remove(order['id'])		
		
class BuyWithAverage(TradingAlgorithm):
    """
    This algorithm uses some really clever math! Höhöhö
    Trying to follow the trend.
    """
    
    def __init__(self, market, broker, portfolio):
        log.debug("Initiating TestingAlgorithm Object")
        self.market = market
        self.broker = broker
        self.portfolio = portfolio
        self.market.data.time_change.registerObserver(self.time_changed)
        #self.broker.order_fill.registerObserver(self.order_filled)
        self.name = 'BuyWithAverage'
        self.latestBars = []
        self.avgBars = 500 #on how many of the latest bars do we calculate an average?
        self.timeout = 1 #only allowed to sell and buy every ... ticks
        self.current = 0 #used to determine which tick we have
        
        
    def time_changed(self, dataHandler):
        self.current += 1
        tick = dataHandler.get_current_tick("EURUSD")
        self.latestBars.append(tick)
        avg = self._get_avg()
        if avg != -1:
            #log.info("Latest " + str(self.avgBars) + " bars average... bid: " 
            #+ str(avg['bid']) + "ask: " + str(avg['ask']))
            if self.current % self.timeout == 0:
                # buy if current ask > avg ask
                if tick['ask'] > avg['ask']:
                    if self.portfolio.enough_available('EUR', 1000):
                        order = {'trader_id':self.name, 'amount': 1000,
                            'fxcode':'EURUSD', 'kind': 'buy', 'type': 'market'}
                        self.broker.order_xchange(order, self.portfolio)
                # sell if current bid < avg bid
                if tick['bid'] < avg['bid']:
                    if self.portfolio.enough_available('USD', 1):
                        order = {'trader_id':self.name, 'amount': 0, 
                            'fxcode':'EURUSD', 'kind': 'sell', 'type': 'market'}
                        self.broker.order_xchange(order, self.portfolio)
                        
    def order_filled(self, order):
        if order['trader_id'] == self.name:
            log.info("One of my orders got filled")
            print(order)
            print(self.portfolio.get_portfolio())

    def _get_avg(self):
        """
        Simply calculates the average of the last self.avgBars bars.
        """
        if len(self.latestBars) >= self.avgBars:
            while len(self.latestBars) > self.avgBars:
                self.latestBars.pop(0)
            avg = {'ask':0, 'bid':0}
            for bar in self.latestBars:
                avg['ask'] += bar['ask']
                avg['bid'] += bar['bid']
            avg['ask'] /= self.avgBars
            avg['bid'] /= self.avgBars
            return avg
                
        else:
            log.info("Not enough bars to calculate an average.")
            return -1 
