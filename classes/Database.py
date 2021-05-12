from MySQLdb import _mysql as MySQL_Connector

class MySQL():
	def __init__(self,host,user,passwd,db):
		self.mysql = MySQL_Connector.connect(host=host,user=user,passwd=passwd,db=db)
		self.db = db

		self._table = None
		self._error = None

	@property
	def table(self):
		return self._table

	@table.setter
	def table(self,name):
		self._table = f"`{self.db}`.`{name}`"

	@property
	def error(self):
		return self._error

	@error.setter
	def error(self,tup):
		self._error = tup

	# Run and return SQL query
	def query(self,sql):
		try:
			self.mysql.query(sql)
			result = self.mysql.store_result()
			return result.fetch_row()
		except Exception as e:
			return repr(e)

	def escape(self,string):
		string = self.mysql.escape_string(string)
		string = string.decode("utf-8")
		return string

	def has_column(self,name):
		name = self.escape(name)
		sql = f"SHOW COLUMNS FROM {self.table} WHERE `{name}` LIKE `{name}`;"
		print(type(self.query(sql)))
		#return self.query(sql)