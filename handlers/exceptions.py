class DatabaseInterfaceError(Exception):
	def __init__(self):
		self.msg = 'Database instance is not derived from the IDatabase abstract base class. Unable to establish connection.'
		
	