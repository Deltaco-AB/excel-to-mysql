from MySQLdb import _mysql as MySQL_Connector

class MySQL():
	def __init__(self,host,user,passwd,db):
		self.mysql = MySQL_Connector.connect(host=host,user=user,passwd=passwd,db=db,charset="utf8")
		self.db = db

		self.engine = "InnoDB"
		self.charset = "utf8mb4"
		self.collate = "utf8mb4_unicode_ci"

		self._table = None

	@property
	def table(self):
		return self._table

	@table.setter
	def table(self,name):
		self._table = f"`{self.db}`.`{name}`"

	# Run and return SQL query
	def query(self,sql,maxrows = 0):
		try:
			self.mysql.query(sql)
			result = self.mysql.store_result()
			return result.fetch_row(maxrows=maxrows)
		except Exception as e:
			return e

	# Return true if an SQL query returned a match
	def truthy(self,result):
		if(isinstance(result,Exception) or len(result) < 1):
			return False
		return True

	def escape(self,string):
		string = self.mysql.escape_string(string)
		string = string.decode("utf-8")
		return string