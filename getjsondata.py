#!/usr/bin/env python
# a small script to get temperature data from MariaDB in json format
# expects argument tablename (table name in database)
# and optional to and from for time series limits
import cgi
import cgitb
import mysql
import mysql.connector
import json
import datetime
from mysql.connector import errorcode
from secrets import databaseuser,databasepassword

cgitb.enable()
print("Content-Type: text/html;charset=utf-8\n")
databasename="iot"
databasehost="127.0.0.1"
databaseport=3306

arguments = cgi.FieldStorage()

#set the borders for the request
to_timestamp="NONE"
tablename="temperature_teleinfo"
if "table" in arguments.keys(): # do it explicitly to avoid SQL injections
    if arguments["table"].value=="temperature_teleinfo":
        tablename="temperature_teleinfo"
    if arguments["table"].value=="teleinfo":
        tablename="teleinfo"
    if arguments["table"].value=="temperature_projectorremote":
        tablename="temperature_projectorremote"

if "to" in arguments.keys():
    to_timestamp=arguments["to"].value
else:
    now=datetime.datetime.now()
    to_timestamp=now.strftime('%Y-%m-%d %H:%M:%S')
    
from_timestamp="NONE"
if "from" in arguments.keys():
    from_timestamp=arguments["from"].value
else:
    #by default display 1 day of data
    dt_object = datetime.datetime.strptime(to_timestamp, '%Y-%m-%d %H:%M:%S')
    dt_object=dt_object-datetime.timedelta(days=1)
    from_timestamp=dt_object.strftime('%Y-%m-%d %H:%M:%S')

mycursor=None
mydb=None
try:
    mydb = mysql.connector.connect(
        database=databasename,
        host=databasehost,
        port=databaseport,
        user=secrets.databaseuser,
        passwd=secrets.databasepassword)
    mycursor = mydb.cursor()

    sql="set @row:=-1; set @numrows:= (SELECT COUNT(*) FROM "+tablename+" WHERE date<%s and date>%s); set @everyNthRow := FLOOR(@numrows/98); SELECT r.* FROM ( SELECT DATE_FORMAT(date, '%Y-%m-%d %H:%i:%S'),temperature FROM "+tablename+" WHERE date<%s AND date>%s ORDER BY date ASC) r CROSS JOIN ( SELECT @i := 0 ) s HAVING ( @i := @i +1) MOD @everyNthRow=1 OR @i=@numrows;"
    itr=mycursor.execute(sql,(to_timestamp,from_timestamp,to_timestamp,from_timestamp),multi=True) # avoid SQL injections
    myresult=None
    for item in itr:
        if item.with_rows:
            myresult=item.fetchall()
    #print mycursor.statement
    x=[j[0] for j in myresult]
    y=[j[1] for j in myresult]
    json_string = json.dumps((x,y))
    print json_string
except mysql.connector.Error as error:
    print("Error")
    print("Error: {}".format(error))
#except mysql.Error as error:     
#    print("MySQL Error {}".format(error))
finally:
    if mycursor!=None:
        mycursor.close()
    if mydb!=None:
        mydb.close()
        





