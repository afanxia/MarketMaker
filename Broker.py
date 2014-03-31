from Portfolio import InDebt, Portfolio
from datetime import timedelta
from numbers import Number
from signals import Signal
import logging as log

class NotEnoughMoney(InDebt):
	def __init__(self, InDebtException, message):
		self.code = InDebtException.code
		self.amount = InDebtEnxception.amount
		self.message = message

class CurrencyNotForTrade(Exception):
	def __init__(self, message):
		self.message = message

class Broker:
	""" Broker handling the Order Dictionaries
		ALL ORDERS dicts have to include keys:
			string fxcode, int `amount`, `kind` ('buy'/'sell'),
			`type` ('market'/'limit')
			LIMIT ORDERS need to contain
			number `limit`, datetime `expires`
	"""
	def __init__(self, market,
		limit_storage_time = timedelta(days=10),
		lag_time = timedelta(milliseconds=500)):
		log.debug("Initiating Broker Object")
		self.market = market

		self.market.data.tick.registerObserver(self.market_tick)
		self.market.data.time_change.registerObserver(self.market_tick)

		self._orders = []
		self._limit_storage_time = limit_storage_time
		self._market_order_lag = lag_time

		self.order_fill = Signal()
		self.order_delete = Signal()

	def get_max_limit_storage_time(self):
		return self._limit_storage_time

	def _make_transaction_xchange(self, portfolio, curr1, amount1, curr2, amount2):
		"""
		"""
		try:
			portfolio.transact(curr1, amount1)
			portfolio.transact(curr2, amount2)
		except InDebt as e:
			raise NotEnoughMoney(e, "You haven't got %f %s. Order can't "
				"be filled" % (e.amount, e.code))

	def _fill_order_xchange(self, order):
		tick = self.market.data.get_current_tick(order['fxcode'])
		curr = self._get_currencies_from_fxcode(order['fxcode'])
		if order['kind'] == 'buy':
			if order['amount'] == 0:
				order['amount'] = order['portfolio'].get_amount(curr[0])
			self._make_transaction_xchange(order['portfolio'], curr[0], 
				-1 * order['amount']/tick['bid'], 
				curr[1], order['amount'])
		elif order['kind'] == 'sell':
			if order['amount'] == 0:
				order['amount'] = order['portfolio'].get_amount(curr[1])
			self._make_transaction_xchange(order['portfolio'], curr[0],
				order['amount']/tick['ask'],
				curr[1], -1 * order['amount'])
		else:
			raise ValueError("order needs to be either sellout or an"
			"amount has to be set")
		self.order_fill.trigger(order)

	def _get_currencies_from_fxcode(self, fxcode):
		if fxcode == 'EURUSD':
			return ('EUR', 'USD')
		else:
			raise CurrencyNotForTrade("Currency %s isn't implemented "
				" in the Broker Class yet. No information to resolve "
				" the fxcode to the single currencies" % fxcode)
	
	def market_tick(self, market):
		"""called on every new tick"""
		self._check_open_orders()

	def order_xchange(self, order, portfolio):
		order.update({'sector':'xchange', 'portfolio': portfolio})
		order = self._check_order(order)
		if order['type'] == 'market':
			order['execute_time'] = (self.market.data.get_current_time()
				+ self._market_order_lag)
		self._orders.append(order)
	
	def _check_open_orders(self):
		for order in self._orders[:]:
			if order['type'] == 'limit':
				if order['expires'] < self.market.data.get_time():
					self.order_delete.trigger(order)
					self._orders.remove(order)
					continue
				if (order['kind'] == 'buy' and 
					self.market.data.get_current_tick(
					order['fxcode'])['bid'][0] >= order['limit'] or
					order['kind'] == 'sell' and 
					self.market.data.get_current_tick(
					order['fxcode'])['ask'][0] <= order['limit']):
					self._fill_order_xchange(order)
					self._orders_remove(order)
			else:
				if order['execute_time'] <= (self.market.
					data.get_current_time()):
					self._fill_order_xchange(order)
					self._orders.remove(order)
				
				
	def _check_order(self, order):
		"""Checks a Order dict if it is a valid order"""
		if order['type'] not in ('limit', 'market'):
			raise ValueError("Order key `type` must be set to either "
				"'market' or 'limit'")
		if order['kind'] not in ('buy', 'sell'):
			raise ValueError("Order key `kind` must be set to either "
				"'buy' or 'sell'")
		
		if order['type'] == 'limit':
			if order['expires'] == None:
				order['expires'] = ( self.market.data.get_current_time()
				+ self._orders_storage_time )
			elif (order['expires'] > ( self._orders_storage_time +
				self.market.data.get_current_time() )or 
				order['expires'] < 0):
				raise ValueError("Expires should be smaller then or equal "
					" to %s and not-negative, you passed '%s' by.",
					self._orders_storage_time, expires)
			if not isinstance(order['limit'], Number):
				raise ValueError("If you pass by a limit order you have"
				"to set a limit")

		return order
