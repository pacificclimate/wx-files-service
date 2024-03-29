# Creating and populating Wx-Files databases

## Overview

A Wx-Files Service database contains an index of the available weather 
files and is the source of metadata for the backend web service.

The databases use the following user names/roles, whose credentials
can be found in the CSG password manager using the search term `wxfs`:
- owner role for database 
- rw role for creating and populating the schema 
- ro role for reading data (backend's access)

This documentation includes instructions for creating a new database and
for using scripts in this project to populate that database. The steps are
- Create a new WxFS database
- Prepare to run scripts
- Create the WxFS schema in the database
- Index files into the database

## Create a new WxFS database

1. Obtain the credentials for the `postgres` user on the database server.
2. Connect to the server with PSQL (or other favorite tool) as user 
`postgres`.
3. Choose a name for the database (typically beginning with `wxfs`). 
   - In general, expect there 
to be one or more pre-existing WxFS databases on the server. This is
because (due to laziness) we create and populate a new database every
time we index a set of files. Indexing is fast. 
   - If you are comfortable with the data loss,
you could empty (or delete) an existing WxFS database to reuse the name.
4. Execute the following SQL:

   ```sql
   CREATE DATABASE <wxfs_database_name>
       WITH 
       OWNER = <wxfs owner role>
       TEMPLATE = template0
       ENCODING = 'UTF8'
       LC_COLLATE = 'en_CA.UTF-8'
       LC_CTYPE = 'en_CA.UTF-8'
       TABLESPACE = pg_default
       CONNECTION LIMIT = -1;
   
   ALTER ROLE wxfs IN DATABASE <wxfs_database_name>
       SET search_path TO public;
   ALTER ROLE wxfs_rw IN DATABASE <wxfs_database_name>
       SET search_path TO public;
   ALTER ROLE wxfs_ro IN DATABASE <wxfs_database_name>
       SET search_path TO public;

   GRANT SELECT ON ALL TABLES IN SCHEMA public TO <wxfs ro role>;
   GRANT ALL ON ALL TABLES IN SCHEMA public TO <wxfs rw role>;
   GRANT ALL ON ALL TABLES IN SCHEMA public TO <wxfs owner role>;
   ```

## Prepare to run scripts

1. If you have not already done so, [Install the project](installation.md) 
and activate the virtual env.

## Create the WxFS schema in the database

Regrettably, the database script is not installed by the project. You have
to run it explicitly with a `python ...` command from the appropriate 
directory.

1. `cd wxfs/database/demo`
2. Obtain the credentials for user `wxfs_rw` on the database server.
3. Find out the host address for the database server 
(presently `dbnorth.pcic.uvic.ca`).
5. Construct the DSN for accessing the database 
(`postgresql://<wxfs rw role>:<password>@dbnorth.pcic.uvic.ca/<wxfs_database_name>` )
6. Create the schema in the database
   ```shell
   python database.py -d <DSN> create
   ```
7. If you wish, you can insert some test records into the database.
But be aware you will have to remove them all before indexing a real set
of weather files into the database.
   ```shell
   python database.py -d <DSN> populate
   ```

## Index files into the database

The indexing scripts are installed by the project and can be used directly
from the command line.

### All files in a master directory

Typically, all the files to be indexed are under a single root 
directory. (Such a root directory contains one or more subdirectories, 
one per "location", which is a province or territory.)

Run:

```shell
for i in <root dir>/*; do \
  index_location_collection -d <DSN> $i; 
done 2>&1 | tee wxfs-indexing.log
```

### Files in scattered directories

If, for some unfathomable reason, files for different locations are in
scattered in widely different directories, you will have to obtain each 
location directory path and do the following for each such path:

```shell
index_location_collection -d <DSN> <path> | tee wxfs-indexing.log
```

Or the equivalent bash scripting to read the location paths out of a file.
