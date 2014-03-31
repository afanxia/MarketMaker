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
	"""Simulate a Stock market, either live or historical with participants"""
	
	def __init__(self, directory, name, TAlgorithm, 
		datahandler, Broker, Portfolio):
		"""Initialize a new Stock Simulation
		
		Parameters:
		string directory - the directory in which the simulator
		string name - the name of this simulation. must be unique. will be
			used as name of the database for this simulation
		TAlgorithm - a class for a trading Algorithm
		DataHandler - a instance of DataHandler class
		Broker - a Broker class
		Portfolio - a Portfolio class
		"""
		
		self.name = name
		self.data = datahandler
		start_port = defaultdict(lambda: 0)
		start_port['EUR'] = 50000
		start_port['USD'] = 0 #shouldn't be nec. since it is a
			#defaultdict, but somehow doesn't work elseways
		self.talgo_port = Portfolio(start_port)
		self.talgo = TAlgorithm(
			self, Broker(self), self.talgo_port )

#		self.database_path = directory + name + '.db'
#		self.conn = lite.connect(database_path)

	def run(self, data_frequency):
		log.info("Starting simulation %s", self.name)
		time_intervall = timedelta(seconds=data_frequency)
		while True == self.data.data_available:
			try:
				self.data.update_current_time(time_intervall)
			except InDebt as e:
				log.info(e.message)
				log.info("The Broker is configured to not allow you "
				"to go in debt in any currency yet. Seems as if you "
				"misscalculated :)")
				print(self.talgo_port.get_portfolio())
		log.info("Game ended, no more Data available")
		print(self.talgo_port.get_portfolio())		
