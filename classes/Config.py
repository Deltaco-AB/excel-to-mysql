import json

config_file = "mysql_config.json"

# Create config file (will overwrite existing)
def create_config():
	config = {
		# MySQL settings
		"server": {
			"mysql_host": "",
			"mysql_user": "",
			"mysql_passwd": "",
			"mysql_db": ""
		},
		"rebuild_tables": True, # Rebuild tables and create if missing
		"chunk_size": 1000, # Number of rows to insert into db at a time
		# Additional work after insertion is done
		"post_processing": {
			"change": {}, # Object with key,value pairs of columns to type cast
			# Create indices (will run after "change")
			"index": {
				"primary": None, # Primary key (post-change),
				"columns": [] # Array of columns to index 
			}
		}
	}

	# Create config file
	f = open(config_file, "w")
	f.write(json.dumps(config,indent=4))
	f.close()

# Attempt to load config from file
def get_config():
	try:
		with open(config_file) as f:
			return json.load(f)
	except IOError:
		create_config()
		print(f"A config file has been created ('{config_file}'). Fill it out and run this script again.")
		exit()
