import logging as log
import os
import sqlite3 as lite
from signals import Signal
from datetime import timedelta
from collections import defaultdict
from pprint import pprint
from Portfolio import InDebt

log.getLogger(__name__)

#log.basicConfig(filename='stock_sim.log',level=log.DEBUG, format=
#	"%(asctime)s || %(levelname)s: %(filename)s:%(lineno)d - %(funcName)s: \
#	%(message)s")


class Market:
	"""Main Class. Runs the Simulation as a whole"""
	
	def __init__(self, TAlgorithm, 
		datahandler, Broker, Portfolio, name):
		"""Initialize a new Stock Simulation
		
		Parameters:
	
		TAlgorithm - A Class which extends TradingAlgorithm. Will be run
			as Trader in this simulation. Look at TradingAlgorithm
			for information about what this class should contain
		DataHandler - An instance of Class extending DataHandler. Look
			at DataHandler class about how this classes should look like
		Broker - A Class which will extend the Broker Class. Look at the
			Broker class about how this classes should look like
		Portfolio - a Reference to the Portfolio class
		string name - name of the simulation. has no use yet
		"""
		
		self.name = name
		self.game_end = Signal()
		self.data = datahandler
		start_port = defaultdict(lambda: 0)
		start_port['EUR'] = 50000
		self.broker = Broker(self)

		self.talgo_port = Portfolio(start_port)
		self.talgo = TAlgorithm(
			self, self.broker, self.talgo_port )

		self.date = None

#		self.database_path = directory + name + '.db'
#		self.conn = lite.connect(database_path)

	def run(self, data_frequency):
		"""Starts and runs the simulation. Will forward in time
			`data_frequency` seconds. The broker will check each tick in
			that time (check if limits are reached etc.). the trading
			algorithm only gets a notification at the end of the forward
			that means, `data_frequency` being 10 would mean, the
			talgorithm would get notificated about new data every 10
			seconds. he could then load all ticks of the last 10 secs
			Parameters:
			number data_frequency - the frequency in which the
				talgorithm gets new data and is able to take action
				upon that data
		"""
		log.info("Starting simulation %s", self.name)
		time_intervall = timedelta(seconds=data_frequency)
		while True == self.data.data_available:
			self.data.update_current_time(time_intervall)
			if self.data.get_current_time().date() != self.date:
				self.date = self.data.get_current_time().date()
				log.info("Today is the %s. Your Portfolio is worth "
				"%f€", self.date,
				self.talgo_port.get_portfolio_value_in_eur(self.data))

		log.info("Game ended, no more Data available")
		self.game_end.trigger()
		print(self.talgo_port.get_portfolio())
		log.info("In EUR your portfolio is worth %f",
			self.talgo_port.get_portfolio_value_in_eur(self.data))
