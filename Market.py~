import logging as log
import os
import sqlite3 as lite
from events import EventHandler, Event

log.getLogger(__name__)

log.basicConfig(filename='stock_sim.log',level=log.DEBUG, format=
	"%(asctime)s || %(levelname)s: %(filename)s:%(lineno)d - %(funcName)s: \
	%(message)s")


class Market:
	"""Simulate a Stock market, either live or historical with participants"""
	
	def __init__(self, directory, name, TAlgorithm, 
		DataHandler, Broker, Portfolio):
		"""Initialize a new Stock Simulation
		
		Parameters:
		string directory - the directory in which the simulator
		string name - the name of this simulation. must be unique. will be
			used as name of the database for this simulation
		TAlgorithm - a class for a trading Algorithm
		DataHandler - a class which will handle and deliver Data
		Broker - a Broker class
		Portfolio - a Portfolio class
		"""
		
		
		TAlgorithm(self, Broker(self), Portfolio({'EUR': 50000}))
		self.data = DataHandler()
		self.database_path = directory + name + '.db'
		self.conn = lite.connect(database_path)

		self.change = Signal()


	def run(self):
		while True == data.data_available:
			self.data.update_data()
			self.market_change(self)
