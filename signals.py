class Signal:

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
