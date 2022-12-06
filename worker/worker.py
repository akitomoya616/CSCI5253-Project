import sys
import redis
import os
import platform

import base64
import glob

import mysql.connector
from mysql.connector import Error
import pandas as pd
import time

pw = 'test1234' # password created in MySQL server

infoKey = "{}.rest.info".format(platform.node())
debugKey = "{}.rest.debug".format(platform.node())

redisHost = os.getenv("REDIS_HOST") or "localhost"
redisPort = os.getenv("REDIS_PORT") or 6379
redisClient = redis.StrictRedis(host=redisHost, port=redisPort, db=0)

# set sql database and table value for later use
sqldatabasename = 'project_database'
deleteTableName = 'DELETED_DATA'
tableName = 'customer'

# connect to SQL server
print("connecting to MySQL server...\n")
mydb = mysql.connector.connect(
        host="mysql", # host name is the name of the container been deployed in .deployment, if everything is running on localhost then it is "localhost"
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
        host="mysql", # host name is the name of the container been deployed in .deployment, if everything is running on localhost then it is "localhost"
        user="root",
        password="test1234",
        database=sqldatabasename)
print("Successfully connected to: " + sqldatabasename + "!\n")

# mycursor = mydb.cursor() # mycursor now reference to the database we pointed to
mycursor = mydb.cursor(buffered=True) # mycursor now reference to the database we pointed to, referenced from https://stackoverflow.com/questions/29772337/python-mysql-connector-unread-result-found-when-using-fetchone

# create the table we need if it does not exist with all column names and data types
# remember to DELETE THE WHOLE TABLE AND RECREATE IT if datatype for an EXISTING column has been changed
# set id as primary key and allow it to be automatically generated everytime we plug in new row
mycursor.execute(f"CREATE TABLE if not exists {tableName} (ID INT NOT NULL AUTO_INCREMENT, Name VARCHAR(255), Product VARCHAR(255), Price DECIMAL(9,3), Date VARCHAR(255), PRIMARY KEY (ID))") # DECIMAL(9,3) means we can have up to 6 places before the decimal and a decimal of up to 3 places
mycursor.execute(f"CREATE TABLE if not exists {deleteTableName} (ID INT)") # only stores deleted id - NOT IN USE RIGHT NOW since now ID for each row will be automatically generated

print("Tables in the current database:")
mycursor.execute("SHOW TABLES")
for x in mycursor:
  print(x)
print()

# Clean out redis value in these key if needed during development process
redisClient.delete("sql_result")
redisClient.delete("sql_command")

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

            # first only get the data from redis instead of poping it right now, do the following normal processes
            current_command_from_redis = redisClient.lindex("sql_command", 0)
            log_debug("print current command value")
            print(current_command_from_redis)

            log_debug("after cleanning name:")
            # clean keyword to match with the one uploaded from rest server
            current_command_from_redis = list(str(current_command_from_redis).replace("b'", '').replace("'",'').split(",")) 
            print(current_command_from_redis)

            command_type = current_command_from_redis[0]

            if (command_type == "INSERT"):
                # create the table again just in case it got deleted later after running into drop table method
                mycursor.execute(f"CREATE TABLE if not exists {tableName} (ID INT NOT NULL AUTO_INCREMENT, Name VARCHAR(255), Product VARCHAR(255), Price DECIMAL(9,3), Date VARCHAR(255), PRIMARY KEY (ID))")
                
                log_debug("entering sql command for insertion!")
                log_debug("assign values gained from sql command")
                type, name, product, price, date = [i for i in current_command_from_redis] # type = INSERT in this case, not gonna be used

                log_debug("generate SQL command")
                print(id, name, product, price, date)
                # INSERT INTO {tableName} (ID, Name, Product, Price, Date)
                # SELECT * FROM (SELECT \'{int(id)}\', \'{name}\', \'{product}\', \'{float(price)}\', \'{date}\') AS tmp     <-- must give value with '' (int and float value can be ignored) so they can bre recognized as value but not column name
                # WHERE NOT EXISTS (
                #     SELECT * FROM {tableName} WHERE Name = \'{name}\' AND Product = \'{product}\' AND Price = \'{float(price)}\' AND Date = \'{date}\'
                # ) LIMIT 1
                sql = f"INSERT INTO {tableName} (Name, Product, Price, Date) SELECT * FROM (SELECT \'{str(name)}\', \'{product}\', \'{float(price)}\', \'{date}\') AS tmp WHERE NOT EXISTS (SELECT * FROM {tableName} WHERE Name = \'{name}\' AND Product = \'{product}\' AND Price = \'{float(price)}\' AND Date = \'{date}\') LIMIT 1"
                log_debug("execute SQL command")
                mycursor.execute(sql)
                mydb.commit()

            elif (command_type == "QUEUE"):
                log_debug("entering sql command for queuing!")
                
                log_debug("generate SQL command")
                sql = f"SELECT * FROM {tableName}"
                log_debug("execute SQL command")
                mycursor.execute(sql)
                mydb.commit()
                myresult = mycursor.fetchall()
                element = []
                for x in myresult:
                    element.append(str(x))
                
                print(str(element))
                # return the result back to REDIS with a different tag for rest server to grab from
                redisClient.lpush("sql_result", *element) 

            elif (command_type == "SUM"):
                log_debug("entering sql command for summarizing!")
                
                log_debug("generate SQL command")
                sql = f"SELECT SUM(Price) FROM {tableName}"
                log_debug("execute SQL command")
                mycursor.execute(sql)
                mydb.commit()
                myresult = mycursor.fetchall()
                sum = myresult[0][0] # [0][0] to get that value from returned list, which is the total price
                print("sum is: " + str(sum))
                
                # return the result back to REDIS with a different tag for rest server to grab from
                redisClient.lpush("sql_result", str(sum)) 
                
            elif (command_type == "SORT"):
                log_debug("entering sql command for queuing!")

                log_debug("assign values gained from sql command")
                type, orderByValue, asc_desc = [i for i in current_command_from_redis] # type = SORT in this case, not gonna be used
                
                log_debug("generate SQL command")
                sql = f"SELECT * FROM {tableName} ORDER BY {orderByValue} {asc_desc}"
                log_debug("execute SQL command")
                mycursor.execute(sql)
                mydb.commit()
                myresult = mycursor.fetchall()
                element = []
                for x in myresult:
                    element.append(str(x))
                
                # return the result back to REDIS with a different tag for rest server to grab from
                redisClient.lpush("sql_result", *element) 
            
            elif (command_type == "DELETE"):
                log_debug("entering sql command for deletion!")
                log_debug("assign values gained from sql command")
                type, table_name, id_to_delete = [i for i in current_command_from_redis] # type = DELETE in this case, not gonna be used
                
                log_debug("generate SQL command")
                sql = f"DELETE FROM {table_name} WHERE ID = {id_to_delete}"
                log_debug("execute SQL command")
                mycursor.execute(sql)
                mydb.commit()
            
            elif (command_type == "DROP"):
                log_debug("entering sql command for dropping!")
                log_debug("assign values gained from sql command")
                type, table_name = [i for i in current_command_from_redis] # type = DROP in this case, not gonna be used

                log_debug("generate SQL command")
                sql = f"DROP TABLE {table_name}"
                log_debug("execute SQL command")
                mycursor.execute("commit ")
                mycursor.execute(sql)
                mydb.commit()

            elif (command_type == "EXTRA"):
                log_debug("entering sql command for extra feature!")
                log_debug("assign values gained from sql command")
                type = [i for i in current_command_from_redis] # type = EXTRA in this case, not gonna be used

                # grab the data from sql table for later trasformation from rows to df format
                # pre-sort the result in asc or desc order so df can create a graph using date from oldest to newest time
                sql_query = pd.read_sql(f"SELECT * FROM {tableName} ORDER BY Date ASC", mydb)
                print(sql_query)

                # Convert SQL to DataFrame
                df = pd.DataFrame(sql_query)
                print("df generated is:")
                print(df)

                # plot a price based on data diagram
                plot = df.plot(x ='Date', y='Price', kind='line')
                fig = plot.get_figure()
                # create a directory under worker directory called pics
                if not os.path.exists('pics'):
                    os.mkdir('pics')
                # and save the diagram genereated in png format in there
                fig.savefig('pics/date_price.png')

                for pic_data in glob.glob("pics/*png"):
                    print('sending pic data to REDIS for rest server to grab from...')

                    # return the result back to REDIS with a different tag for rest server to grab from
                    redisClient.lpush("sql_result", base64.b64encode( open(pic_data, "rb").read() ).decode('utf-8')) 
                    
                    # send the next data after 1 second
                    time.sleep(1)

            else:
                log_debug("not a valid sql command!")
            
            log_debug("finish processing, exiting sql command!")
            redisClient.rpop("sql_command")

            print()
            print()

except Exception as e:
    print(e) # print the error report if we faced the exception
    log_info("exception raised: " + str(e))
