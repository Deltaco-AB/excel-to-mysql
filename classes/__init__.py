from .Job import Worker
from .Excel import Excel
from .Database import Database
from .Config import get_config

excel_dir = "sheets/"

# Import config from file or generate
db_config = get_config()

# Connect to database
db = Database(db_config["server"]["mysql_host"],db_config["server"]["mysql_user"],db_config["server"]["mysql_passwd"],db_config["server"]["mysql_db"])

class Globals():
	@staticmethod
	def get_excel_list():
		return excel_dir

	@staticmethod
	def db_connect():
		return db

	@staticmethod
	def get_db_host():
		return db_config["server"]["mysql_host"]
