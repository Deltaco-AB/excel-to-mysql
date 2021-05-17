# Excel to MySQL

A strict one-to-one importer of Excel `.xlsx` files to MySQL tables.

The [post-processor functions](#basic-import-with-post-processing) enables fine tuning of the imported data such as type casting and indexing.

## Installation

### Prerequisites

- [Python 3.8 or newer](https://www.python.org/)
- [pip3 for Python 3](https://pip.pypa.io/en/stable/installing/)

*You can install pip3 on Debian/Ubuntu with*
```
sudo apt-get install python3-pip
```

---

#### Debian/Ubuntu

1. Clone or [download a zip](https://github.com/Deltaco-AB/excel-to-mysql/archive/refs/heads/master.zip) of this repo
```bash
git clone https://github.com/Deltaco-AB/excel-to-mysql.git
```
2. `cd` into the project directory and run the following to install all system dependencies
```bash
cat requirements.system | xargs sudo apt-get install
```
3. Install Python dependencies with `pip3`
```bash
python3 -m pip install -r requirements.txt
```

## Basic usage (Quick import)

Import one or more Excel file(s).

1. Place your `.xlsx` file(s) in the `sheets/` directory.
2. Run `import_all.py`
```bash
python3 import_all.py
```
3. A config file called `mysql_config.json` has been created in the project root dir.
4. Enter your MySQL credentials under the `server` section. Everything else can be left as default.
```json
"server": {
  "mysql_host": "IP_OR_HOSTNAME:CUSTOM_PORT",
  "mysql_user": "MYSQL_USERNAME",
  "mysql_passwd": "MYSQL_PASSWORD",
  "mysql_db": "MYSQL_DATABASE"
}
```

---

**If `rebuild_tables` is `true` (which is the default setting), a MySQL user with [these privileges](#standard-privileges) are required**

Setting this value to `false` will append columns and rows to an already existing database and table, in which case; [these privileges](#base-privileges) are required.

---

5. Run `import_all.py` again and if everything is configured correctly, the import should now start.
```bash
python3 import_all.py
```

## Basic import with post-processing

**Perform the steps in the [basic usage](#basic-usage-quick-import) guide first. These functions are run after each imported Excel**

---

### Type casting

This script uses [`pandas.DataFrame.dtypes`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.dtypes.html) to determine the data type for each column.

A translation is performed to convert pandas data types to SQL data types (`datetime64[ns]` becomes `DATE` etc.). It's more than likely that the data type provided by pandas and the translation done on it afterwards can differ from the actual data type. You can therefore define columns in your `mysql_config.json` where the data type is known, and will be changed after insertion is done.

*example:*
```json
"post_processing": {
  "change": {
    "I_am_a_String": "VARCHAR(256)",
    "I_am_not_a_Float": "DOUBLE"
  }
}
```

### Indexing

#### Primary key

The table created will exist without a primary key. You can define a column name in your `mysql_config.json` to use as primary key

*example:*
```json
"post_processing": {
  "index": {
    "primary": "uuid"
  }
}
```

#### Additional indices

You can define columns to create indices for by specifying them by name in your `mysql_config.json`

*example:*
```json
"post_processing": {
  "index": {
    "columns": [
      "ItemID",
      "SearchKeywords",
      "AvailableFlag"
    ]
  }
}
```

## MySQL Privileges

### Base Privileges

The following MySQL privileges are required to run this script.

Data|Structure|Administraton
--|--|--
`INSERT`|`ALTER`|
`UPDATE`

### Standard Privileges

The following MySQL privileges are required to run this script with `rebuild_tables`, which is recommended and enabled by default.

Data|Structure|Administraton
--|--|--
`INSERT`|`ALTER`|
`UPDATE`|`INDEX`|
||`DROP`|
||`CREATE`|

