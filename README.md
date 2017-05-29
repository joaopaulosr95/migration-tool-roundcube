# migration-tool-roundcube

## Description
This is a Python script for migrating Roundcube users from one database to another one. In case the destination database is already running, the script also handles the generation of a new id for each user and ensuring its relationships will also be updated.

## Dependencies
The project relies on Python 2.7 and its pip dependencies are listed in the [requeriments](requeriments.txt) file.

**Editor's choice**: If you are running Debian-based distros, you better simply run the following command
``` shell
$ sudo apt-get install python-dev libmysqlclient-dev python-mysqldb
```

## Usage
To run the program, you just need to run the main.py file passing the right parameters. Let's take a look at them:

|Parameter|Description|
|:---:|:---:|
|db1host|MySQL host where the data is stored|
|--db1port PORT (optional)|MySQL port in db1host (default: 3306)|
|db1user|MySQL username in db1host|
|db1passwd|MySQL passwd in db1host|
|--db1name DB (optional)|Name of database where data is stored (default: roundcubemail)|
|db2host|MySQL host where the data will be stored|
|--db2port PORT (optional)|MySQL port in db2host (default: 3306)|
|db2user|MySQL username in db1host|
|db2passwd|MySQL passwd in db2host|
|--db2name DB (optional)|Name of database where data will be stored (default: roundcubemail)|
|--domain DOMAIN|If you don't want a full migration, you can specifiy a wildcard domain to migrate\ i.e. "all users that have username like @example.com"|
|--skip-contacts|Use this parameter if you only want user accounts to be migrated, but not their contacts|

Here is an simple (and most common) example of a full migration for the domain "example.com" from host 10.0.0.1 to host 10.0.0.3. Both use port 3306 to host MySQL and store data in roundcubemail database:
``` shell
$ python -m tests.migrationtool 10.0.0.1 admin secret \
    10.0.0.3 admin secret --domain "example.com"
```

And now a more advanced example. Here we have two MySQL servers using different ports than 3306
and which will not migrate contacts, just users:
``` shell
$ $ python -m tests.migrationtool 10.0.0.1 --db1port 33060 admin secret \
    10.0.0.3 --db2port 33061 admin secret --domain "example.com" --skip-contacts
```
