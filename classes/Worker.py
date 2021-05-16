import time

# Data type translation lookup table
datatypes = {
	"str": "TEXT",
	"NaTType": "VARCHAR",
	"int": "INT",
	"int64": "INT",
	"float": "FLOAT",
	"float64": "DOUBLE",
	"bool_": "BOOLEAN",
	"Timestamp": "DATE",
}

class Job():
	def __init__(self,db,excel):
		self.db = db
		self.data = excel.dataframe
		self.columns = excel.get_headers()

		self._chunk_size = 100

		# Use first column as primary key
		primary = self.columns[0]
		self.db.append_column(primary)
		self.db.make_unique(primary)

	@property
	def chunk_size(self):
		return self._chunk_size

	@chunk_size.setter
	def chunk_size(self,size):
		self._chunk_size = size

	def truncate(self):
		print(f"Table {self.db.table} is about to get wiped (truncated) for data-entry. Interrupt within 10 seconds to abort.")
		time.sleep(10)
		self.db.truncate()

	# Create database columns from Excel headers
	def create_columns(self):
		columns = {}
		for column in self.columns:
			# Let first item for Excel header determine the column data type
			datatype = type(self.data[column][0]).__name__

			# Treat unknown data types as strings
			if(datatype not in datatypes):
				datatype = "str"

			# Translate Python (panda) types to SQL types
			columns[column] = datatypes[datatype]
		
		self.db.append_columns(columns)
		self.db.drop_column(self.db.placeholder) # Remove placeholder column

	# Create database insertable list from Excel rows
	def insert_rows(self):
		rows = []

		for index in range(1,len(self.data)):
			# Dispatch chunks for database insertion when threshold is satisfied
			if(index % self.chunk_size == 0):
				self.db.insert_rows(rows)
				rows = []

			values = []
			for column in self.columns:
				values.append(self.data[column][index])
			rows.append(values)

		# Insert remaining rows
		if(len(rows) > 0):
			self.db.insert_rows(rows)

	def run(self):
		self.create_columns()
		self.insert_rows()