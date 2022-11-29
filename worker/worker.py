import sys
import redis
import os
import platform
from minio import Minio

import glob

import mysql.connector
from mysql.connector import Error
import pandas as pd

pw = 'test1234' # password created in MySQL server
infoKey = "{}.rest.info".format(platform.node())
debugKey = "{}.rest.debug".format(platform.node())

redisHost = os.getenv("REDIS_HOST") or "localhost"
redisPort = os.getenv("REDIS_PORT") or 6379
redisClient = redis.StrictRedis(host=redisHost, port=redisPort, db=0)

minioHost = os.getenv("MINIO_HOST") or "localhost:9000"
minioUser = os.getenv("MINIO_USER") or "rootuser"
minioPasswd = os.getenv("MINIO_PASSWD") or "rootpass123"
bucketname='CSCI5253-Project'

# set minio host and port for connection
minioHost = os.getenv("MINIO_HOST") or "localhost:9000"
minioUser = os.getenv("MINIO_USER") or "rootuser"
minioPasswd = os.getenv("MINIO_PASSWD") or "rootpass123"

minioClient = Minio(minioHost,
               secure=False,
               access_key=minioUser,
               secret_key=minioPasswd)

bucketname='CSCI5253-Project' # for minio bucket setup and reference

# set sql database and table value for later use
sqldatabasename = 'TEST_DB' #'project_database'
deleteTableName = 'DELETED_DATA'
tableName = 'customer'

# connect to SQL server
print("connecting to MySQL server...\n")
mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="test1234")
mycursor = mydb.cursor() # mycursor now reference to the whole sql server
print("Successfully connected to the SQL database!\n")

# create a database in this SQL server
mycursor.execute("CREATE DATABASE IF NOT EXISTS " + sqldatabasename)
print("Current databases in the SQL server are:")
mycursor.execute("SHOW DATABASES")
for x in mycursor:
  print(x)
print()

# connect to the specific database
mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="test1234",
        database=sqldatabasename)
print("Successfully connected to: " + sqldatabasename + "!\n")

mycursor = mydb.cursor() # mycursor now reference to the database we pointed to

# create the table we need if it does not exist with all column names and data types
# remember to DELETE THE WHOLE TABLE AND RECREATE IT if datatype for an EXISTING column has been changed
mycursor.execute(f"CREATE TABLE if not exists {tableName} (ID INT, Name VARCHAR(255), Product VARCHAR(255), Price DECIMAL(9,3), Date VARCHAR(255))") # DECIMAL(9,3) means we can have up to 6 places before the decimal and a decimal of up to 3 places
mycursor.execute(f"CREATE TABLE if not exists {deleteTableName} (ID INT)") # only stores deleted id

print("Tables in the current database:")
mycursor.execute("SHOW TABLES")
for x in mycursor:
  print(x)
print()

def log_debug(message, key=debugKey):
    print("DEBUG:", message, file=sys.stdout)
    redisClient = redis.StrictRedis(host=redisHost, port=redisPort, db=0)
    redisClient.lpush('logging', f"{debugKey}:{message}")

def log_info(message, key=infoKey):
    print("INFO:", message, file=sys.stdout)
    redisClient = redis.StrictRedis(host=redisHost, port=redisPort, db=0)
    redisClient.lpush('logging', f"{infoKey}:{message}")

try:
    while (True):

        if (redisClient.llen("sql_command") > 0 ):
            print("Found sql command in redis, start processing!")
            print()

            # assign the current data with a new id
            mycursor.execute(f"SELECT COUNT(*) FROM {tableName}")
            previous_id = mycursor.fetchall() # return in form as [(value,)], shows the current number of rows in table
            print("previous id is: " + str(previous_id))
            mycursor.execute(f"SELECT COUNT(*) FROM {deleteTableName}")
            deleted_id_count = mycursor.fetchall() # return in form as [(value,)], shows the current number of rows in table
            print("total count of deleted id is: " + str(deleted_id_count))
            id = previous_id[0][0] + deleted_id_count[0][0] + 1 # [0][0] to get that value from returned list, which is the last row's id, 
                                                                # + count of deleted id so that new value's id will NEVER replace an existing or used id
                                                                # + 1 to get current row's id that we are going to add into the table
                                                                # e.g. if we have 4 ids in table, remove the 4th one, then add 4 more
                                                                # the result will be 1, 2, 3, 5, 6, 7, 8
                                                                # but not            1, 2, 3, 4, 5, 6, 7
            print("therefore id assigned for current data is: " + str(id) + "\n")

            # first only get the data from redis instead of poping it right now, do the following normal processes
            current_command_from_redis = redisClient.lindex("sql_command", 0)
            log_debug("print current command value")
            print(current_command_from_redis)

            log_debug("after cleanning name:")
            # clean keyword to match with the one uploaded in rest server
            current_command_from_redis = list(str(current_command_from_redis).replace("b'", '').replace("'",'').split(",")) 
            print(current_command_from_redis)

            log_debug("assign values gained from sql command")
            name, product, price, date = [i for i in current_command_from_redis]

            log_debug("generate SQL command")
            # INSERT INTO table_listnames (name, address, tele)
            # SELECT * FROM (SELECT 'Rupert', 'Somewhere', '022') AS tmp
            # WHERE NOT EXISTS (
            #     SELECT name FROM table_listnames WHERE name = 'Rupert'
            # ) LIMIT 1;

            # INSERT INTO {tableName} (ID, Name, Product, Price, Date)
            # SELECT * FROM (SELECT \'{int(id)}\', \'{name}\', \'{product}\', \'{float(price)}\', \'{date}\') AS tmp     <-- must give value with '' (int and float value can be ignored) so they can bre recognized as value but not column name
            # WHERE NOT EXISTS (
            #     SELECT * FROM {tableName} WHERE Name = \'{name}\' AND Product = \'{product}\' AND Price = \'{float(price)}\' AND Date = \'{date}\'
            # ) LIMIT 1
            print(id, name, product, price, date)
            sql = f"INSERT INTO {tableName} (ID, Name, Product, Price, Date) SELECT * FROM (SELECT \'{int(id)}\', \'{str(name)}\', \'{product}\', \'{float(price)}\', \'{date}\') AS tmp WHERE NOT EXISTS (SELECT * FROM {tableName} WHERE Name = \'{name}\' AND Product = \'{product}\' AND Price = \'{float(price)}\' AND Date = \'{date}\') LIMIT 1"
            mycursor.execute(sql)
            mydb.commit()

            
            redisClient.rpop("sql_command")

            print()
            print()

except Exception as e:
    print(e) # print the error report if we faced the exception
    log_info("exception raised: " + str(e))
