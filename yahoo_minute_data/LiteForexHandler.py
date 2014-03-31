import sqlite3 as lite
from pandas import DataFrame
from DataHandler import DataHandler
import logging as log
from collections import defaultdict

log.basicConfig(level=log.DEBUG, format=
	('%(asctime)s || %(levelname)s: %(filename)s:%(lineno)d - %(funcName)s: '
		'%(message)s'))

class MyException:

	def __init__(self, message):
		self.message = message

class DBEmpty(MyException):
	""""""
class NotEnoughDataAvailable(MyException):
	""""""
class LiteForexHandler(DataHandler):

	def __init__(self, sqllite_db, db_tablename = 'forex',
		base_currency = None, limit = 50):
		self.base_currency = base_currency
		self._db = lite.connect(sqllite_db)
		self._db_table = db_tablename
		self._limit = limit
		self._last_loaded_entry = 0
		self._loaded_forex_data = defaultdict(list)
		for forex_code in self._iterate_forex_codes():
			self._loaded_forex_data[forex_code] = DataFrame(
				columns=['ask', 'bid', 'time'])

		self._current_row = 0

		self.data_avaiable = True

	def _iterate_forex_codes(self):
		cursor = self._db.cursor()
		cursor.execute("SELECT code FROM %s GROUP BY code;" % self._db_table)
		for row in cursor.fetchall():
			yield row[0]


	def _load_from_db(self):
		"""Load the next self._limit entries from the Database into a
			panda DataFrame
		"""
		for forex_package in self._get_next_forex():
			for currency in forex_package:
				new_row = {'ask':currency[1],
					'bid':currency[2], 'time':currency[3]}
				self._loaded_forex_data[currency[0]] = (
				self._loaded_forex_data[currency[0]].append(
					new_row, ignore_index=True) )
	
	def _get_next_forex(self):
		"""Iterate through Forex Data. Return all forex data for a certain time
		"""
		cursor = self._db.cursor()
		cursor.execute( ("SELECT time FROM %s GROUP BY time "
			"ORDER BY time ASC LIMIT %d, %d;") % 
			(self._db_table, self._last_loaded_entry, self._limit) )
		self._last_loaded_entry += self._limit
		forex_packages = 0

		for row in cursor.fetchall():
			forex_packages += 1
			cursor.execute("SELECT code,ask,bid,time FROM %s WHERE time='%s'"
				% (self._db_table, row[0]) )
			yield cursor.fetchall()
			
		if 0 == forex_packages:
			raise DBEmpty("No more entries left to retrieve. Simulation ends")
		

	def update_data(self):
		"""Push the latest Forex Data to the Object, so that we move one step
			further in time. get_latest_data will now return next data
		"""
		if self._current_row == self._last_loaded_entry:
			try:
				self.load_from_db()
			except DBEmpty as e:
				log.info(e.message)
				self.data_avaiable = False
				raise
		self._current_row += 1

		
	def get_latest_forex_by_code(self, forex_code, n = 1):
		"""
		Returns the last N forex data entries from the forex_codes list
		"""
		if n < 1:
			raise Exception("n needs to be a natural, positive number (>0)")
		elif n > time:
			raise DataVolumeNotAvailable("Tried to retrieve last %d forex data"
			" entries, but only %d available" % (n, self._current_row))
		elif forex_code not in self._loaded_forex_data:
			raise DataTypeNotAvailable("Tried to retrieve forex rates for %s "
			"which isn't part of the Data this Handler is offering")

		return self._loaded_forex_data[forex_code][self._current_row - n + 1:self._current_row]


	def get_latest_forex(self, current_currency, to_currency, n = 1):
		"""get the last n ask/bid rates and the time at which they where
			loaded as a panda DataFrame (columns are 'ask', 'bid' and 'time', 
			last row is newest). n=1 will only return last rates
			Parameters:
			string current_currency,to_currency - Currency Representations
			int n - last n ask/bid rates will be returned
		"""
		try:
			rate = self.get_latest_forex_by_code(current_currency + 
				to_currency, n)
		except DataTypeNotAvailable:
			try:
				rate_other_direct = self.get_latest_forex_by_code(to_currency +
					current_currency, n)
				rate['bid'] = 1 / rate_other_direct['ask']
				rate['ask'] = 1 / rate_other_direct['bid']
				rate['time'] = rate_other_direct['time']
				log.warning("Due to mathematical operations on the rate, the "
					"rate %s is possibly not accurate"
					% current_currency + to_currency)
			except DataTypeNotAvailable:
				if None != self.base_currency:
					curr_rate = self.get_latest_forex_by_code(current_currency
						+ base_currency, n)
					to_rate = self.get_latest_forex_by_code(base_currency +
						to_currency, n)
					rate = (to_rate[['ask', 'bid']] 
						* curr_rate[['ask', 'bid']])
					rate['time'] = curr_rate['time']
					log.warning("Due to mathematical operations on the "
						"rate, the rate %s is possibly not accurate"
						% current_currency + to_currency)
				else:
					raise
		return rate

	def get_time():
		"""The whole time system is kinda messed up, every single entry stores
			the time. Have to do that better next time
		"""
		any_forex = next(iter(self._loaded_forex_data))
		return any_forex['time'][self._current_row]
		
