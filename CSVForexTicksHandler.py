import pandas as pd
import os, os.path
from signals import Signal
from DataHandler import DataHandler
from collections import defaultdict
from datetime import datetime
import logging as log

log.basicConfig(level=log.DEBUG, format=
	('%(asctime)s || %(levelname)s: %(filename)s:%(lineno)d - %(funcName)s: '
		'%(message)s'))

class DataNotAvailable(Exception):

	def __init__(self, message):
		self.message = message

class NoMoreDataAvailable(DataNotAvailable):
	""""""

class CSVForexTicksHandler(DataHandler):
	
	def __init__(self, directory, fxcodes, time = None):
		self._directory = directory
		self._data = defaultdict(None)
		self.fxcodes = fxcodes
		self.data_available = True

		self.time_change = Signal()
		self.tick = Signal()

		self._comb_index = None
		self._load_files(self._directory, self.fxcodes)
		
		if None == time:
			self._time = self._comb_index[0]
		else:
			self._time = time
		self._start_time = self._time

	def _load_files(self, directory, fxcodes):
		log.info("Start loading CSV...")
		for fxcode in self.fxcodes:
			self._load_file(fxcode,
				os.path.join(self._directory, '%s.csv' % fxcode)
			)
			log.info("Loaded %s", fxcode)
		log.info("Finished loading CSV")

		log.info("Sorting loaded data")
		for fxcode in self.fxcodes:
			self._data[fxcode] = ( self._data[fxcode]
				.reindex(index=self._comb_index, method='pad') )
		log.info("Finished sorting")

	def _load_file(self, fxcode, filepath):
		self._data[fxcode] = pd.io.parsers.read_csv(
			filepath,
			header=0, index_col=0,
			usecols = [0,1,2],
			names=['datetime','ask','bid'],
			parse_dates=True,
			date_parser = self.date_parser #TODO: this takes ages!
		)
		if self._comb_index is None:
			self._comb_index = self._data[fxcode].index
		else:
			self._comb_index.union(self._data[fxcode].index)	
		
	def date_parser(self, data):
		return datetime.strptime(data, '%Y%m%d %H%M%S%f')

	def _iterate_time_points(self):
		for time in self._comb_index:
			yield time
	
	def update_data_time(self, time):
		"""
		Updates the time at which the simulation is. Will forward current time,
		afterwards all data until current time will be availabe
		Parameters:
		timedelta time - the time which you want to forward
		"""
		if self._time + time > self._comb_index[-1]:
			log.warning("Couldn't forward time by %s, data is only available "
				"until %s. Will forward %s", time, self._comb_index[-1],
				self._comb_index[-1] - self._time)
			time = self._comb_index[-1] - self._time
			self.data_available = False
		time_temp = self._time
		for timepoint in self._comb_index[time_temp: time_temp + time]:
			self._time = timepoint
			self.tick.trigger(self)
		self._time = time
		self.time_change.trigger(self)

			
	def get_latest_data(self, fxcode, time):
		"""Get all ticks for symbol in last time. 
		Paramters:
		timedelta time - get latest data in time
		"""
		if time > self._time - self._start_time:
			raise DataNotAvailable("You tried to retrieve data for last %s. "
				"Only data for last %s is available" % (time, 
				self._time - self._start_time) )
		return self._data[fxcode][self._time - time : self._time]
		
	def get_current_tick(self, fxcode):
		"""Return current tick
		"""
		n = -1
		while self._data[fxcode][n]['ask'] == NaN:
			n -= 1
		return self._data[fxcode][n]
