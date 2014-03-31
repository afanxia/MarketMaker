import pandas.io.data as web
from pandas import DataFrame
import sqlite3 as lite
import datetime
import logging as log
from collections import defaultdict
from time import sleep
from urllib.parse import urlencode
from urllib.request import urlopen
import json

#filename='stock_sim.log',
log.basicConfig(level=log.INFO, format=
	('%(asctime)s || %(levelname)s: %(filename)s:%(lineno)d - %(funcName)s: '
		'%(message)s'))


#opening times in UTC
#opening_times = defaultdict(list)
#opening_times['NASDAQ']['open'] = datetime.time(15,30)
#opening_times['NASDAQ']['close'] = datetime.time(22,0)

class SymbolNotInDB(Exception):
	def __init__(self, symbol):
		self.symbol = symbol

class YahooScraper:
	"""Scrape Data from Yahoo into a SQLITE3 Database"""

	def __init__(self, symbols = [], forex = [], database = 'yahoofinance.db'):
		self.yql_api = 'http://query.yahooapis.com/v1/public/yql?'
		self.yot_xchange = ( 'http://www.datatables.org/'
			'yahoo/finance/yahoo.finance.xchange.xml')

		self.symbols = symbols
		self.forex_codes = forex

		for symbol in self.symbols:
			try:
				self.get_quote(symbol)
			except SymbolNotInDB as e:
				log.exception('Yahoo doesn\'t provide information for Symbol '
					'%(symbol)s. Won\'t scrape data for %(symbol)s'
					% {'symbol':e.symbol} )
				self.symbols.remove(symbol)

		self.curr_quotes = defaultdict(list)				

		self.db = lite.connect(database)
		cursor = self.db.cursor()
		cursor.execute('''CREATE TABLE IF NOT EXISTS stocks(
			ID INTEGER PRIMARY KEY,
			symbol TEXT,
			price REAL,
			short_ratio REAL,
			time DATETIME
			);''')

		cursor.execute('''CREATE TABLE IF NOT EXISTS forex(
			ID INTEGER PRIMARY KEY,
			code TEXT,
			rate REAL,
			ask REAL,
			bid REAL,
			time DATETIME
			);''')
		self.db.commit()


	def get_quote(self, symbol):
		"""Retrieve the Quote from Yahoo using pandas"""
		quote = web.get_quote_yahoo(symbol)
		if 0 == quote['last'][0]:
			raise SymbolNotInDB(symbol)
		return quote

	def save_current_data(self):
		cursor = self.db.cursor()
		cursor.executemany("INSERT INTO stocks (symbol, price, \
			short_ratio, time) VALUES (?,?,?,?)",
			[(symbol, quote['last'], quote['short_ratio'], str(self.time)) 
			for symbol, quote in self.curr_quotes.iterrows() ] )
		cursor.executemany("INSERT INTO forex (code, rate, \
			ask, bid, time) VALUES (?,?,?,?,?)",
			[(code, forex['Rate'], forex['Ask'], forex['Bid'], 
			str(forex['Time'])) 
			for code, forex in self.curr_forex.iterrows() ] )
		self.db.commit()
		
	def list_to_string(self, convertion_list):
		"""Convert ['This', 'That', 'Test'] to '"This", "That", "Test"' for
			SQL IN Statement"""
		list_as_string = ""
		for string in convertion_list:
			list_as_string += '"%s",' % string
		return list_as_string[:-1]
		
			
	def get_forex(self, currency_symbols, format = 'json'):
		"""Retrieve the current exchange Rate of two currencies"""
		query = '''USE "%s" AS yahoo.xchange;
			SELECT * FROM yahoo.xchange WHERE pair in (%s);
			''' % (self.yot_xchange, self.list_to_string(currency_symbols))
		params = urlencode({'q':query, 'format':'json'})
		req = urlopen(self.yql_api + params)
		
		encoding = req.headers.get_content_charset()
		result = json.loads( req.read().decode(encoding) )['query']

		df_result = DataFrame(result['results']['rate']).set_index('id')
		df_result['Time'] = datetime.datetime.strptime(result['created'], 
			'%Y-%m-%dT%H:%M:%SZ')
		return df_result
		

	def run(self, frequency):
		while True:
			self.start_time = datetime.datetime.now()
			log.info("Scraping Data at %s" % self.start_time)

			if self.symbols:
				self.curr_quotes = web.get_quote_yahoo(self.symbols)
			self.time = datetime.datetime.utcnow()
			if self.forex_codes:
				self.curr_forex = self.get_forex(self.forex_codes)

			log.debug(self.curr_forex)
			log.debug(self.curr_quotes)


			log.debug("Difference between times: %s" 
				% (self.time - self.start_time).total_seconds())
			self.save_current_data()
			sleep(frequency - 
				(datetime.datetime.now() - self.start_time).total_seconds() )
	
