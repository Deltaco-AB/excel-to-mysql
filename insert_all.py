from pathlib import Path

from classes.Excel import Excel
from classes.Database import Database
from classes.Config import get_config
from classes.Job import Worker

excel_dir = "sheets/"

db_config = get_config() # Import db config from file or generate
db = Database(db_config["server"]["mysql_host"],db_config["server"]["mysql_user"],db_config["server"]["mysql_passwd"],db_config["server"]["mysql_db"])

# Get all xlsx files from the current directory
xlsx_files = list(Path(excel_dir).glob("*.xlsx"))

# Convert all found xlsx files
for xlsx in xlsx_files:
	excel = Excel(xlsx) # Load xlsx
	excel_name = xlsx.name.replace(".xlsx","") # Get file name without extension

	# Use the extensionless file name as table name in the selected db
	db.table = excel_name

	# Drop and re-create table
	if(db_config["rebuild_tables"]):
		db.drop()
		db.create_table()

	job = Worker(db,excel)
	job.run()

	# Perform additional work defined in config
	job.post_processing(db_config)