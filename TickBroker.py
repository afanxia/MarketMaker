from Portfolio import InDebt, Portfolio
from datetime import timedelta
from numbers import Number
from signals import Signal
import logging as log
from Broker import Broker

class NotEnoughMoney(InDebt):
	def __init__(self, InDebtException, message):
		self.code = InDebtException.code
		self.amount = InDebtEnxception.amount
		self.message = message

class CurrencyNotForTrade(Exception):
	def __init__(self, message):
		self.message = message

class TickBroker(Broker):
	""" Broker handling the Order, which are represented by python
		Dictionaries
		For TAlgos, if you pass an order to TickBroker.order_xchange,
		ALL ORDERS dicts have to include keys:
			string fxcode, int `amount`, `kind` ('buy'/'sell'),
			`type` ('market'/'limit')
			LIMIT ORDERS need to contain
			number `limit`, datetime `expires`
	"""
	def __init__(self, market,
		limit_storage_time = timedelta(days=10),
		lag_time = timedelta(milliseconds=500)):
		"""Initialize the broker
			Parameters:
			Market market - a market instance
			timedelta limit_storage_time - a time span which limit
				orders will be saved maximum
			timdelta lag_time - the time which it will take to broker
				to actually set a market order
		"""
		log.debug("Initiating Broker Object")
		self.market = market

		self.market.data.tick.registerObserver(self.market_tick)
		self.market.data.time_change.registerObserver(self.market_tick)

		self._orders = {}
		self._limit_storage_time = limit_storage_time
		self._market_order_delay = lag_time

		self.order_fill = Signal()
		self.order_delete = Signal()
		self._newest_order_id = -1

	def get_max_limit_storage_time(self):
		return self._limit_storage_time

	def _make_transaction_xchange(self, portfolio, curr1, amount1,
		curr2, amount2):
		"""Makes the actuall transaction in the portfolio
			ParametersL
			Portfolio portfolio - a portfolio instance on which the
				transaction will happen
			string curr1,2 - the currency codes (e.g. 'EUR') on which
				the holdings should change
			numer amount1,2 - amount`i` is the number which will be
				added to your holdings of curr`i`

			Normally either curr1 or curr2 will be negative and the
			other one positive, because this is normally a transaction
			from one currency into another
		"""
		try:
			portfolio.transact(curr1, amount1)
			portfolio.transact(curr2, amount2)
		except InDebt as e:
			raise NotEnoughMoney(e, "You haven't got %f %s. Order can't "
				"be filled" % (e.amount, e.code))

	def _fill_order_xchange(self, order):
		"""Fill an order. Check if it is sell or buy, calculate the
			price for the given amount that should be bought/sold
			and then make the transaction
			Parameters:
			dict order - a dicitonary representing an order
		"""
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
		"""Make an Limit or Market order. Return the `order_id` which
			the TAlgo can use to recognize the order later.
			This method will only append the order to self._orders,
			the actuall execution is done in _check_open_orders later
		"""
		self._newest_order_id += 1
		order.update({'sector':'xchange', 'portfolio': portfolio})
		order = self._check_order(order)
		if order['type'] == 'market':
			order['execute_time'] = (self.market.data.get_current_time()
				+ self._market_order_delay)
		self._orders[self._newest_order_id] = order
		return self._newest_order_id
	
	def _check_open_orders(self):
		"""Run through all orders in self._orders and check if they
			expired or need to be executed. limit orders will be
			executed when `limit` is reachend and deleted if `expires`
			date is reached. Market orders will be executed after the
			market order delay (simulates delay of your internet
			connection) passed by. If order is executed or deleted, it
			extends the order with the order-id so that the TAlgo
			will recieve it in the event trigger and then deletes it
		"""
		for order_id, order in list(self._orders.items()):
			if order['type'] == 'limit':
				if order['expires'] < self.market.data.get_time():
					order['id'] = order_id
					self.order_delete.trigger(order)
					del self._orders[order_id]
					continue
				if (order['kind'] == 'buy' and 
					self.market.data.get_current_tick(
					order['fxcode'])['bid'][0] >= order['limit'] or
					order['kind'] == 'sell' and 
					self.market.data.get_current_tick(
					order['fxcode'])['ask'][0] <= order['limit']):
					order['id'] = order_id
					self._fill_order_xchange(order)
					del self._orders[order_id]
			else:
				if order['execute_time'] <= (self.market.
					data.get_current_time()):
					order['id'] = order_id
					self._fill_order_xchange(order)
					del self._orders[order_id]
				
				
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
