import logging as log

class InDebt(Exception):
	def __init__(self, code, amount):
		self.code = code
		self.amount = amount

class Portfolio:

	def __init__(self, starting_portfolio):
		"""Parameters:
		dict starting_portfolio - needs to be an instance of defaultdict(lambda: 0)
		"""
		log.debug("Initation Portfolio Object")
		self._holdings = starting_portfolio
		
	def get_amount(self, code):
		"""Return owned amout of paper referenced by `code`"""
		return self._holdings[code]

	def get_portfolio(self):
		return self._holdings
		
	def transact(self, code, amount):
		if self._holdings[code] + amount < 0:
			raise InDebt(code, amount)
		self._holdings[code] += amount
		
	def enough_available(self, code, amount):
		if self._holdings[code] >= amount:
			return True
		else:
			return False
