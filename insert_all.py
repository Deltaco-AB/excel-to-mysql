from pathlib import Path

from classes.Excel import Excel
from classes.Database import MySQL
from classes.Config import get_config

excel_dir = "sheets/"

db_config = get_config() # Import db config from file or generate
db = MySQL(db_config["mysql_host"],db_config["mysql_user"],db_config["mysql_passwd"],db_config["mysql_db"])

# Get all xlsx files from the current directory
xlsx_files = list(Path(excel_dir).glob("*.xlsx"))

# Convert all found xlsx files
for xlsx in xlsx_files:
	excel = Excel(xlsx)
	db.table = "FILES"

	print(db.has_column("FILE_NAME"))