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

# Contains bulk variants of methods defined in Database class
# These methods follow an arbitrary protocol for parsing data
class BulkTools():
	# Append multiple columns at once
	# Protocol:
	# - Expects a list of string key, value pairs
	# - key = column name
	# - value = colum type (SQL)
	def append_columns(self,columns):
		queries = []
		for column_name,column_type in columns.items():
			# Don't add columns that exist in db
			if(self.column_exists(column_name)):
				continue

			# Apply length to columns of type VARCHAR
			if(column_type == "VARCHAR"):
				column_type = f"VARCHAR({self.default_length})"
			
			queries.append(f"ADD `{column_name}` {column_type} NOT NULL")
		
		# Concat all queries and execute
		queries = ",".join(queries)
		sql = f"ALTER TABLE {self.table} {queries};"
		return self.bquery(sql)

	def insert_rows(self,row_values,columns = None):
		# Add prepending and appending `
		def wrap_column(column):
			return f"`{column}`"
		
		# Get columns from database if no columns were passed
		if(not columns):
			columns = self.get_columns()
		
		# Create a SQL query CSV from column names
		columns = list(map(wrap_column,columns)) # Add string seperators
		columns_sql = ",".join(columns) # Join columns with a comma

		# Create a SQL query VALUES list (CSV) from rows
		rows = []
		for row in row_values:
			values = []
			# Values for each column in order
			for value in row:
				value = str(value)
				value = self.escape(value)

				# Add the value for this row as a string ''
				values.append(f"'{value}'")

			values = ",".join(values) # Create an SQL array from values on this row
			rows.append(f"({values})") # Add the stringified SQL array to list of rows
		
		values = ",".join(rows) # Stringify all rows as a CSV of each array

		sql = f"INSERT INTO {self.table} ({columns_sql}) VALUES {values};"
		return self.bquery(sql)

class Database(MySQL,BulkTools):
	def __init__(self,host,user,passwd,db):
		super(Database,self).__init__(host,user,passwd,db)
		self.default_length = 256
		self.placeholder = "table_filler"

	# Execute query and return bool of the success state
	def bquery(self,sql):
		result = self.query(sql,1)
		return self.truthy(result)

	# Check if table exists in the current database
	def table_exists(self,name = None):
		# Check current table if argument list is empty
		if(not name):
			name = self.table.split("`.`") # Get table name from `db`.`table`
			name = name[1][:-1] # Strip last `
		
		name = self.escape(name)
		sql = f"SHOW TABLES LIKE '%{name}%';"
		return self.bquery(sql)

	def get_columns(self):
		if(not self.table_exists()):
			return False
		
		columns_sql = f"SHOW COLUMNS FROM {self.table}"
		result = self.query(columns_sql)
		columns = []
		
		for column in result:
			columns.append(column[0].decode("utf-8"))

		return columns

	# Check if column exists in the selected table
	def column_exists(self,name):
		name = self.escape(name)
		sql = f"SHOW COLUMNS FROM {self.table} LIKE '{name}';"
		return self.bquery(sql)

	# Create basic table in the selected database
	def create_table(self):
		if(self.table_exists()):
			return False
		
		sql = f"CREATE TABLE {self.table} (`{self.placeholder}` INT NULL) CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_unicode_ci' ENGINE = {self.engine};"
		return self.bquery(sql)

	# Append new column
	def append_column(self,name,data_type = "int",length = -1):
		if(self.column_exists(name)):
			return False

		if(length < 0):
			length = self.default_length
		
		name = self.escape(name)
		sql = f"ALTER TABLE {self.table} ADD `{name}` {data_type.upper()}({length}) NOT NULL;"
		return self.bquery(sql)

	# Set column as primary key
	def make_unique(self,column,update = False):
		if(update):
			# Update existing primary key
			sql = f"ALTER TABLE {self.table} DROP PRIMARY KEY, ADD PRIMARY KEY(`{column}`)"
			return self.bquery(sql)
		else:
			# Add new primary key
			sql = f"ALTER TABLE {self.table} ADD PRIMARY KEY(`{column}`)"
			if(not self.bquery(sql)):
				# Attempt to update existing if query fails
				self.make_unique(column,True)

	def drop_column(self,column):
		sql = f"ALTER TABLE {self.table} DROP `{column}`";
		return self.bquery(sql)

	def truncate(self):
		sql = f"TRUNCATE {self.table}"
		return self.bquery(sql)

	def drop(self):
		sql = f"DROP {self.table}"
		return self.bquery(sql)
