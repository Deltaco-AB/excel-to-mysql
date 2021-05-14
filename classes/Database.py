from MySQLdb import _mysql as MySQL_Connector

class MySQL():
	def __init__(self,host,user,passwd,db):
		self.mysql = MySQL_Connector.connect(host=host,user=user,passwd=passwd,db=db)
		self.db = db
		self.engine = "InnoDB"

		self._table = None

	@property
	def table(self):
		return self._table

	@table.setter
	def table(self,name):
		self._table = f"`{self.db}`.`{name}`"

	# Run and return SQL query
	def query(self,sql):
		try:
			self.mysql.query(sql)
			result = self.mysql.store_result()
			return result.fetch_row()
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

class Database(MySQL):
	def __init__(self,host,user,passwd,db):
		super(Database,self).__init__(host,user,passwd,db)

	# Execute a query and return a bool of the success state
	def binary_query(self,sql):
		result = self.query(sql)
		return self.truthy(result)

	# Check if a table exists in the current database
	def table_exists(self,name = None):
		# Check current table if argument list is empty
		if(not name):
			name = self.table.split("`.`") # Get table name from `db`.`table`
			name = name[1][:-1] # Strip last `
		
		name = self.escape(name)
		sql = f"SHOW TABLES LIKE '%{name}%';"
		return self.binary_query(sql)

	# Check if a column exists in the selected table
	def column_exists(self,name):
		name = self.escape(name)
		sql = f"SHOW COLUMNS FROM {self.table} LIKE '{name}';"
		return self.binary_query(sql)

	# Create a basic table in the selected database
	def create_table(self):
		if(self.table_exists()):
			return False
		
		sql = f"CREATE TABLE {self.table} (`table_filler` INT(0) NULL) ENGINE = {self.engine};"
		return self.binary_query(sql)

	def append_column(self,name,data_type = "int",length = 256):
		sql = f"ALTER TABLE {self.table} ADD `{name}` {data_type.upper()}({length}) NOT NULL;"
		return self.binary_query(sql)
