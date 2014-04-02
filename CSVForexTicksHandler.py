import pandas as pd
import os, os.path
from signals import Signal
from DataHandler import DataHandler
from collections import defaultdict
from datetime import datetime
import logging as log
from numbers import Number
from numpy import isnan

#log.basicConfig(level=log.DEBUG, format=
#	('%(asctime)s || %(levelname)s: %(filename)s:%(lineno)d - %(funcName)s: '
#		'%(message)s'))

class DataNotAvailable(Exception):
	"""Exception to be thrown when Data is requested which isn't
	available, e.g. because it is to far in the past or it is a
	symbol which isn't available. Maybe more specific exceptions should
	be added in the future
	"""
	def __init__(self, message):
		self.message = message

class CSVForexTicksHandler(DataHandler):
	"""The first used DataHandler. It reads a CSV file in this format:
		time, ask, bid, where time is formated as %Y%m%d %H%M%S%f
		The Data which this Handler was written for is the CSV Tick
		Data from http://histdata.com
		__Important functions provided:__
		.update_current_time(time)
		.get_latest_data(time)
		.get_current_time()
		.get_current_tick()
		for detailed explainaition look at the functions

		__Important Signals__
		self.time_change
			when this is triggered, the handler has moved forward in
			time and new data is available. To be implemented by TAlgos
			so they know when new data is available, so they can read
			the data and take action upon it
		self.tick
			this is triggered on every new tick, that means every single
			update of a ask/bid price of any fxcode. this should not be
			implemented by a TAlgo, since it is unrealistic! It is used
			by the broker, e.g. to check if limits are reached
		
	"""

	
	def __init__(self, directory, fxcodes, time = None):
		"""Initialize the Handler.
			Parameters:
			string directory - the directory which the .csv files lay in
			list fxcodes - a list of strings which represent currency
				pairs, e.g. ['EURUSD', 'USDJPY']. the Handler will look
				into the directory provided by `directory`, if it can
				find files called `fxcode`.csv (where fxcode is an
				item in fxcodes), e.g. EURUSD.csv
			datetime time - the time at which the simulation should
				start at, if not provided, it just uses the first time
				available
		"""
	
		log.debug("Initiating CSVForexTicksHandler Object")
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
		"""load all files in directory which belong to a fxcode and
			saves them to self._data[fxcode] as panda DataFrame. e.g. if 
			fxcodes is [`EURUSD`, `USDJPY`] and directory 
			'~/Documents/data/' it would look for 
			'~/Documents/data/EURUSD.csv' and
			'~/Documents/data/USDJPY.csv', load them and save them to
			self._data['EURUSD'] and self._data['USDJPY'] as panda
			DataFrame.
			When everything is loaded, update each panda dataframe to
			use the combined index as a index.
		"""
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
		""" load a csv file and save it to self._data.
			then update the combined index self._comb_index which in
			the end will contain every singe datetime where a tick in
			any of the loaded currency pairs occured
		"""
		self._data[fxcode] = pd.io.parsers.read_csv(
			filepath,
			header=0, index_col=0,
			usecols = [0,1,2],
			names=['datetime','ask','bid'],
			parse_dates=True,
			date_parser = self.date_parser 
		)
		if self._comb_index is None:
			self._comb_index = self._data[fxcode].index
		else:
			self._comb_index.union(self._data[fxcode].index)	
		
	def date_parser(self, data):
		return datetime(int(data[0:4]), int(data[4:6]), int(data[6:8]),
						int(data[9:11]), int(data[11:13]), int(data[13:15]),
						int(data[15:18])*1000) #expects microsecond, we've mili

	def update_current_time(self, time):
		"""
			Forward the simulation in time. Look for every tick that
			has happened between now and the time you want to forward 
			to, update the time to that tick and trigger self.tick
			At the end trigger self.time_change when reached the point 
			in time you want to forward to
			updates
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

		for timepoint in self._comb_index[self._comb_index
			.slice_indexer(time_temp, time_temp + time)]:
			self._time = timepoint
			self.tick.trigger(self)

		self._time = time_temp + time
		self.time_change.trigger(self)

			
	def get_latest_data(self, fxcode, time):
		"""Return all ticks that happened between now and now - time as
			a pandas DataFrame
		Paramters:
		timedelta time - if this would be 20 secs, you would get all
			data from the last 20 secs
		"""
		if time > self._time - self._start_time:
			raise DataNotAvailable("You tried to retrieve data for last" 
				" '%s'.Only data for last '%s' is available" % (time, 
				self._time - self._start_time) )
		return self._data[fxcode][self._time - time : self._time]
		
	def get_current_tick(self, fxcode):
		"""Return the freshest bid/ask price which is available. Go back
			in time from the current time. Find the freshest tick which
			affected the currency pair referenced by `fxcode`
		"""

		'''get the length of the DataFrame up to current moment
		 = the current row-number in the DataFrame of all data for
		fxcode which we are at.
		'''
		row_location = self._data[fxcode][:self._time].shape[0] - 1
		i = 0
		#go back until you find a column which actually contains data
		while isnan(self._data[fxcode]['ask'].irow(row_location - i)):
			i += 1
			if i > row_location:
				raise DataNotAvailable("No data available for '%s' "
					"the moment. It will probably be available later "
					"in time" % fxcode)

		return self._data[fxcode].irow(row_location - i)

	def get_current_time(self):
		return self._time
