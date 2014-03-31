import logging as log
import os
import sqlite3 as lite
from signals import Signal
from datetime import timedelta

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
		TAlgorithm(self, Broker(self), Portfolio({'EUR': 50000}))

#		self.database_path = directory + name + '.db'
#		self.conn = lite.connect(database_path)

	def run(self, data_frequency):
		log.info("Starting simulation %s", self.name)
		time_intervall = timedelta(seconds=data_frequency)
		while True == self.data.data_available:
			self.data.update_current_time(time_intervall)
