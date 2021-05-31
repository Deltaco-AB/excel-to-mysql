from pathlib import Path
from classes import *

excel_dir = Globals.get_excel_list()
db = Globals.db_connect()

# Get all xlsx files from the current directory
xlsx_files = list(Path(excel_dir).glob("*.xlsx"))

# Convert all found xlsx files
for xlsx in xlsx_files:
	print(f"Building DataFrame from '{xlsx.name}'..")
	excel = Excel(xlsx) # Load xlsx
	excel_name = xlsx.name.replace(".xlsx","") # Get file name without extension

	# Use the extensionless file name as table name in the selected db
	db.table = excel_name

	print(f"Rebuilding table {db.table}..")

	# Drop and re-create table
	if(db_config["rebuild_tables"]):
		db.drop()
		db.create_table()

	job = Worker(db,excel,db_config)
	job.run()

	# Perform additional work defined in config
	print("Finishing up..")
	job.post_processing(db_config)

	print(f"\nExcel sheet from '{xlsx.name}' has been inserted into: [{Globals.get_db_host()}%{db.table}]")