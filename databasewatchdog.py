import mysql.connector
from mysql.connector import errorcode
import time
import smtplib
from secrets import databaseuser, databasepassword,email,emailserver,emailport,emailuser,emailpassword

databasename="iot"
databasehost="127.0.0.1"
databaseport=3307

def sendemail(subject, message):
    header  = 'From: %s\n' % email
    header += 'To: %s\n' % email
    header += 'Subject: %s\n\n' % subject
    message = header + message
    server = smtplib.SMTP(emailserver,emailport)
    server.starttls()
    server.login(emailuser, emailpassword)
    problems = server.sendmail(email, email, message)
    server.quit()

def checkTable(tablename):
    try:
        mydb = mysql.connector.connect(
                database=databasename,
                host=databasehost,
                port=databaseport,
                user=databaseuser,
                passwd=databasepassword)
        mycursor = mydb.cursor()
        sql= "SELECT date FROM "+tablename+" ORDER BY date DESC LIMIT 1;"
        print "executing ", sql
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
    except mysql.connector.Error as error:
        print "Error"
        print "Error: {}".format(error)
    except mysql.Error as error:     
        print "MySQL Error {}".format(error)
    finally:
         mycursor.close()
         mydb.close()
         
    if len(myresult)!=1:
        print "ERROR: not enough/too many rows for ", tablename, len(myresult)
        return False
    if len(myresult[0])!=1:
        print "ERROR: not enough/too many rows for ", tablename, len(myresult[0])
        return False
    mysqltime=myresult[0][0]
    entryfound=True
    hoursago=-1
    try:
        databasetime=time.strptime(str(mysqltime), '%Y-%m-%d %H:%M:%S')
        nowtime = time.localtime()
        difftime=time.mktime(nowtime) - time.mktime(databasetime)
        print "Last database entry", difftime/60, " min ago"
        if difftime>86400: #after 1 day alarm
            entryfound=False
            print "Last entry is very old, sending e-amil"
            hoursago=diffimte/(60.*60.)
    except ValueError:
        entryfound=False

    #test cases
    #entryfound=False
    #hoursago=1237321/(60.*60.)
        
    if not entryfound:
        sendemail("Database Watchdog: last entry in table "+tablename+" is "+str(hoursago)+" hours old.","This is the database watchdog from sherpa. The last entry in table "+tablename+" is "+str(hoursago)+" hours old.")
        
    return True

if __name__ == "__main__":
    checkTable("teleinfo")
    checkTable("temperature_teleinfo")
    checkTable("temperature_projectorremote")
