import paho.mqtt.client as mqtt
import json
import mysql.connector
from mysql.connector import errorcode
from secrets import mqttuser, mqttpassword, databaseuser, databasepassword

mqttclientid="PythonMQTTDatabaseClient"
mqtthost="localhost"
mqttport=8883
databasename="iot"
databasehost="127.0.0.1"
databaseport=3307

def writeTemperatureToDataBase(message, devicename):
    if devicename!="teleinfo" and devicename !="projectorremote":
        print "ERROR: unknown devicename ", devicename, " for temperature recording"
        return False
    
    #remove all character after last }
    message="}".join(message.split("}")[0:-1])+"}"

    try:
        json_object = json.loads(message)
    except ValueError, e:
        print "not correct json",e

    #check that all fields are available
    if not "temperature" in json_object or not "humidity" in json_object:
        print "ERROR: temperature or humidity not found in json message", json_object, message, devicename
        return False
    
    try:
        mydb = mysql.connector.connect(
                database=databasename,
                host=databasehost,
                port=databaseport,
                user=databaseuser,
                passwd=databasepassword)
        mycursor = mydb.cursor()
        sql = "INSERT INTO temperature_"+devicename+" (temperature, humidity) VALUES (%s, %s)"
        val = (json_object["temperature"], 
               json_object["humidity"])
        print "executing ", sql, val
        mycursor.execute(sql, val)
        mydb.commit()

    except mysql.connector.Error as error:
        print "Error"
        print "Error: {}".format(error)
    except mysql.Error as error:     
        print "MySQL Error {}".format(error)
    finally:
         mycursor.close()
         mydb.close()
    return True
        
def writeTeleInfoToDataBase(message):
    #remove all character after last }
    message="}".join(message.split("}")[0:-1])+"}"

    try:
        json_object = json.loads(message)
    except ValueError, e:
        print "not correct json",e

    #check that all fields are available
    if not "ADCO" in json_object or not "OPTARIF" in json_object or not "ISOUSC" in json_object or not "BASE" in json_object or not "PTEC" in json_object or not "IINST" in json_object or not "IMAX" in json_object or not "PAPP" in json_object or not "MOTDETAT" in json_object:
        print "ERROR: not all fields found in teleinfo json message not found in json message", json_object, devicename
    
    try:
        mydb = mysql.connector.connect(
                database=databasename,
                host=databasehost,
                port=databaseport,
                user=databaseuser,
                passwd=databasepassword)
        mycursor = mydb.cursor()
        sql = "INSERT INTO teleinfo (ADCO, OPTARIF, ISOUSC, BASE, PTEC, IINST, IMAX, PAPP, MOTDETAT) VALUES (%s, %s,%s,%s,%s,%s,%s,%s,%s)"
        val = (json_object["ADCO"], 
               json_object["OPTARIF"],
               json_object["ISOUSC"],
               json_object["BASE"],
               json_object["PTEC"],
               json_object["IINST"],
               json_object["IMAX"],
               json_object["PAPP"],
               json_object["MOTDETAT"])
        print "executing ", sql, val
        mycursor.execute(sql, val)
        mydb.commit()
    except mysql.connector.Error as error:
        print "Error"
        print "Error: {}".format(error)
    except mysql.Error as error:     
        print "MySQL Error {}".format(error)
    finally:
         mycursor.close()
         mydb.close()
    
def on_connect(mqttc, obj, flags, rc):
    print("rc: " + str(rc))


def on_message(mqttc, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    if msg.topic=="teleinfo/teleinfo":
        writeTeleInfoToDataBase(msg.payload)
    if msg.topic=="teleinfo/temperature":
        writeTemperatureToDataBase(msg.payload,"teleinfo")
    if msg.topic=="projectorremote/temperature":
        writeTemperatureToDataBase(msg.payload,"projectorremote")

def on_publish(mqttc, obj, mid):
    print("mid: " + str(mid))


def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(mqttc, obj, level, string):
    print(string)

if __name__ == "__main__":
    mqttc = mqtt.Client(mqttclientid)
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe
    # Uncomment to enable debug messages
    # mqttc.on_log = on_log
    mqttc.username_pw_set(mqttuser, password=mqttpassword)
    mqttc.tls_set(ca_certs=None, certfile=None, keyfile=None, ciphers=None)
    mqttc.tls_insecure_set(True)
    mqttc.connect(mqtthost, mqttport, 60)
    mqttc.subscribe("#", 0)
    mqttc.loop_forever()
