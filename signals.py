class Signal:
	"""A class which does something similar to the observer-pattern.
		You can add this class to your object and other objects will
		be able to register themself as observers. You can call trigger
		to inform all observers that some event took place
	"""
	def __init__(self):
		self._callbacks = []

	def registerObserver(self, callback):
		if callback not in self._callbacks:
			self._callbacks.append(callback)
		else:
			raise ValueError("You can't register the same callback twice")
			
	def trigger(self, *args):
		for callback in self._callbacks:
			callback(*args)
