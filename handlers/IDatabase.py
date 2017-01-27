from abc import ABCMeta, abstractmethod, abstractproperty

class IDatabase(object):
	__metaclass__ = ABCMeta
	
	@abstractproperty
	def connection(self):
		pass

	'''@abstractmethod
	def createAccount(self):
		raise NotImplementedError()
		
	@abstractmethod
	def login(self):
		raise NotImplementedError()'''
		
	