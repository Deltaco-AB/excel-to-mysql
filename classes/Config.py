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
		"create_tables": True # Attempt to create missing tables in DB
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
