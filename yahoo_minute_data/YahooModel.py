"""Helperfunctions for interaction with the Yahoo Finance API using pandas and
	YQL for retrieving stock quotes and forex rates. Always returns
"""
from pandas import DataFrame, io.data as web

def get_forex(currency_symbols):
	"""Retrieve the current exchange Rate of two currencies"""
	yot_xchange = ( 'http://www.datatables.org/'
			'yahoo/finance/yahoo.finance.xchange.xml')
	query = '''USE "%s" AS yahoo.xchange;
		SELECT * FROM yahoo.xchange WHERE pair in (%s);
		''' % (yot_xchange, list_to_string(currency_symbols))
	params = urlencode({'q':query, 'format':'json'})
	req = urlopen('http://query.yahooapis.com/v1/public/yql?' + params)
	
	encoding = req.headers.get_content_charset()
	result = json.loads( req.read().decode(encoding) )['query']

	df_result = DataFrame(result['results']['rate']).set_index('id')
	df_result['Time'] = datetime.datetime.strptime(result['created'], 
		'%Y-%m-%dT%H:%M:%SZ')
	return df_result
	
def get_quote(symbol):
	"""Retrieve the Quote from Yahoo using pandas"""
	quote = web.get_quote_yahoo(symbol)
	if 0 == quote['last'][0]:
		raise SymbolNotInDB(symbol)
	return quote

def list_to_string(convertion_list):
	"""Convert ['This', 'That', 'Test'] to '"This", "That", "Test"' for
		SQL IN Statement"""
	list_as_string = ""
	for string in convertion_list:
		list_as_string += '"%s",' % string
	return list_as_string[:-1]
