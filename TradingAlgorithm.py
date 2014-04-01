from abc import ABCMeta, abstractmethod

class TradingAlgorithm:
	""" The trading Algorithm Class - Parts of this documentation
		are out-dated! Better look at Market, Broker and your
		Datahandler



		will be initialized by market object like this:
		TradingAlgorithm(market-instance, broker-instance, portfolio-instance)
	
		Marke.data is a DataHandler Instance

		Market.data
			.get_latest_forex(curr1, curr2, n)
				get the last n ask/bid rates and the time at which they where
				loaded as a panda DataFrame (columns are 'ask', 'bid' and 
				'time', last row is newest). n=1 will only return last rates
		
			.get_time()
				maybe not necessary, practice will show. if not, will be del
				returns the current time, e.g. for comparing with the time 

		Market.change.registerObserver(callback)
			register function callback to be called when 
			market.data.get_latest_forex was updated and will contain new data
			will be called with callback(market-instance). but market-instance
			is delivered on initializiation too, so prbly won't need it
			
		Broker
			.market_order_xchange(portfolio, order)
				place a market order. trader should	be a `self` reference to 
				your instance of the algorithm
			.limit_order_xchange(portfolio, order)
				place a limit order
			.order_fill.registerObserver(callback)
			.order_delete.registerObserver(callback)
				again, register callback functions of your algorithm to be
				notified when one of your orders is filled or deleted due to
				expire date. callback(order) will be
				called. check if order is actually an order you have made
				earlier, because later on maybe more then one TradingAlgorithm
				will participate in a simulation, so it could be an order from
				someone else
				
		Order is always a dictionary with these keys:
			`curr1`, `curr2` - the currency codes (e.g. 'EUR' or 'USD')
			`amount` - positive amount: buy `amount` curr2 for curr1
					 - negative amount: sell `amount` curr1 for curr2
			in case you are placing a limit order, these keys need to defined
			too:
			`expire` - DateTime instance, e.g. 3 hours. not a point in time but
				a time period
			`limit` - positive number: the limit you want to buy/sell for
			You can (should) define as much other keys as you want,
			e.g. an `trader-id` so you can recognize the order when it is 
			passed back by to your order_fill or order_delete callback and 
			check if it belongs to you etc.
			
		Portfolio
			.get_amount(currency_code)
				get amount you hold of the currency referenced by 
				`currency_code`
			.get_portfolio()
				get your whole portfolio as a dict[currency_code] = amount
			.enough_available(currency_code, amount)
				check if you have got left `amount` of currency referenced by
				`currency_code` (a shortcut you can use in if-statements)
	"""

	__metaclass__ = ABCMeta
