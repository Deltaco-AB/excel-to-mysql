import time

# Data type translation lookup table
datatypes = {
	"object": "TEXT",
	"int": "VARCHAR",
	"int64": "VARCHAR",
	"float": "VARCHAR",
	"float64": "VARCHAR",
	"bool": "BOOLEAN",
	"datetime64[ns]": "DATE",
}

class Post_Processing():
	def __init__(self,config):
		self.config = config["post_processing"]

	# Type cast columns (SQL CHANGE)
	def change(self):
		change = self.config["change"]

		if(len(change.keys()) > 0):
			for column,datatype in change.items():
				self.db.change(column,datatype)

	def primary_key(self):
		column = self.config["index"]["primary"]
		if(not column):
			return False

		return self.db.make_unique(column)

	def index(self):
		columns = self.config["index"]["columns"]

		if(len(columns) < 1):
			return False

		for column in columns:
			self.db.make_index(column)

class Worker(Post_Processing):
	def __init__(self,db,excel):
		self.db = db
		self.data = excel.dataframe
		self.columns = excel.get_headers()

		self._chunk_size = 100

	@property
	def chunk_size(self):
		return self._chunk_size

	@chunk_size.setter
	def chunk_size(self,size):
		self._chunk_size = size

	# Post processing invoker and sequencer
	def post_processing(self,config):
		super(Worker,self).__init__(config)
		self.change()
		self.primary_key()
		self.index()

	# Create database columns from Excel headers
	def create_columns(self):
		columns = {}
		for column in self.columns:
			# Let first item for Excel header determine the column data type
			datatype = str(self.data[column].dtype)

			# Treat unknown data types as pandas object (string)
			if(datatype not in datatypes):
				datatype = "object"

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
				value = self.data[column][index]
				values.append(value)
			rows.append(values)

		# Insert remaining rows
		if(len(rows) > 0):
			self.db.insert_rows(rows)

	def run(self):
		self.create_columns()
		self.insert_rows()