from Portfolio import InDebt, Portfolio

class NotEnoughMoney(InDebt):
	def __init__(self, InDebtException, message):
		self.code = InDebtException.code
		self.amount = InDebtEnxception.amount
		self.message = message

class Broker:
	""" Broker handling the Order Dictionaries
		Order dicts have to include keys:
		curr1, curr2, expires, amount
	"""
	def __init__(self, market, orders_storage_time = 50):
		self.market = market
		self.market.change.registerObserver(self.market_change)
		self._orders = []
		self._orders_storage_time = orders_storage_time
		self.order_fill = Signal()
		self.order_delete = Signal()

	def _open_order(self, order):
		"""Open an order
			Parameters:
			dict Order - Dict with keys 
		"""

	def _fill_order_xchange(self, portfolio, curr1, amount1, curr2, amount2):
		"""fill an order. amount positive -> buy curr2 for curr1, negative ->
		"""
		try:
			portfolio.transact(curr1, amount1)
			portfolio.transact(curr2, amount2)
		except InDebt as e:
			raise NotEnoughMoney(e, "You haven't got %f %s. Order can't "
				"be filled" % (e.amount, e.code))

	def market_order_xchange(self, order, portfolio = None):
		if portfolio == None:
			if is_instance(order['portfolio'], Portfolio):
				portfolio = order['portfolio']
			else:
				raise ValueError("You need to pass by an Portfolio instance")
		if order['amount'] > 0:
			rate = self.market.data.get_latest_forex(order['curr2'], 
				order['curr1'])
			self._fill_order(portfolio, order['curr1'], 
				-1 * order['amount'] * rate['ask'][0], 
				order['curr2'], order['amount'])
		else:
			rate = self.market.data.get_latest_forex(order['curr1'], 
				order['curr2'])
			self._fill_order(portfolio, order['curr1'], -1 * order['amount'], 
				order['curr2'], order['amount'] * rate['bid'][0])
		self.order_filled.trigger(order)
				
	def limit_order_xchange(self, order, portfolio):
		if not isinstance( amount, (int, long, float)) or amount == 0:
			raise ValueError("Amount needs to be numeric and not 0. You passed"
				" %s" % amount)
		if order['expires'] == None:
			order['expires'] = self._orders_storage_time
		elif (order['expires'] > self._orders_storage_time or 
			order['expires'] < 0):
			raise ValueError("Expires should be smaller then or equal to %s"
				" and not-negative, you passed '%s' by.",
				self._orders_storage_time, expires)

		order.update({'sector':'xchange', 'type':'limit', 
			'portfolio': portfolio})
		self._orders.extend({'type':'xchange', 'curr1': curr1, 'curr2': curr2,
			'amount': amount, 'limit':limit, 'trader':trader, 'expires': 
			self.market.data.get_time() +self._orders_storage_time})
	
	def market_change(self, market):
		self._check_open_orders()
		
	def _check_open_orders(self):
		for order in self._orders[:]:
			if order['expires'] < self.market.data.get_time():
				self.order_deleted.trigger(order)
				self._orders.remove(order)
				continue
			if (order['amount'] > 0 and 
				self.market.data.get_latest_forex(order['curr2'],
				order['curr1'])['ask'][0] <= order['limit']):
				self.market_order_xchange(order)
			elif (order['amount'] < 0 and 
				self.market.data.get_latest_forex(order['curr1'],
				order['curr2'])['bid'][0] >= order['limit']):
				self.market_order_xchange(order)
				
				
				
				
