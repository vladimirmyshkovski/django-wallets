def shared_task(func, *args, **kwargs):

	def apply(*args, **kwargs):
		func(*args, **kwargs)
		return True

	def apply_async(*args, **kwargs):
		func(*args, **kwargs)
		return True		

	def delay(*args, **kwargs):
		func(*args, **kwargs)
		return True 

	def wrapper(*args, **kwargs):

		def inner(*args, **kwargs):
			setattr(wrapper, 'apply', apply)
			return func

		return inner()

		return wrapper			