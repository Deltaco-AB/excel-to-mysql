from .Database_MySQL import MySQL

coercive_datatype = {
	"TRUE": "1",
	"FALSE": "0",
	"NAT": "NULL",
	"NAN": "NULL"
}

# Contains bulk variants of methods defined in Database class
# These methods follow an arbitrary protocol for parsing data
class Database_BulkTools():
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
			
			queries.append(f"ADD `{column_name}` {column_type}")
		
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

				# Translate data types to value
				if(value.upper() in coercive_datatype):
					values.append(coercive_datatype[value.upper()])
					continue

				# Add the value for this row as a string ''
				values.append(f"'{value}'")

			values = ",".join(values) # Create an SQL array from values on this row
			rows.append(f"({values})") # Add the stringified SQL array to list of rows
		
		values = ",".join(rows) # Stringify all rows as a CSV of each array

		sql = f"INSERT INTO {self.table} ({columns_sql}) VALUES {values};"
		return self.bquery(sql)

class Database(MySQL,Database_BulkTools):
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
		
		sql = f"CREATE TABLE {self.table} (`{self.placeholder}` INT NULL) CHARACTER SET {self.charset} COLLATE {self.collate} ENGINE = {self.engine};"
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
			sql = f"ALTER TABLE {self.table} DROP PRIMARY KEY, ADD PRIMARY KEY(`{column}`);"
			return self.bquery(sql)
		else:
			# Add new primary key
			sql = f"ALTER TABLE {self.table} ADD PRIMARY KEY(`{column}`);"
			result = self.bquery(sql)
			if(not result):
				# Attempt to update existing if query fails
				self.make_unique(column,True)
			return result

	def make_index(self,column):
		sql = f"ALTER TABLE {self.table} ADD INDEX(`{column}`);"
		return self.bquery(sql)

	def change(self,column,datatype):
		sql = f"ALTER TABLE {self.table} CHANGE `{column}` `{column}` {datatype} CHARACTER SET {self.charset} COLLATE {self.collate} NULL DEFAULT NULL;"
		return self.bquery(sql)

	def drop_column(self,column):
		sql = f"ALTER TABLE {self.table} DROP `{column}`;";
		return self.bquery(sql)

	def truncate(self):
		sql = f"TRUNCATE TABLE {self.table};"
		return self.bquery(sql)

	def drop(self):
		sql = f"DROP TABLE {self.table};"
		return self.bquery(sql)
