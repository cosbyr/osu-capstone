import psycopg2
import urlparse
import os
import abc
from IDatabase import IDatabase

class PostgresDatabase(IDatabase):
	@property
	def connection(self):
		urlparse.uses_netloc.append("postgres")
		url = urlparse.urlparse(os.environ["DATABASE_URL"])

		conn = psycopg2.connect(
			database=url.path[1:],
			user=url.username,
			password=url.password,
			host=url.hostname,
			port=url.port
		)
		
		return conn
		