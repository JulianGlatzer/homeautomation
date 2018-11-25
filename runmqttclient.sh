#!/bin/bash

prc=`ps aux | grep "python mqttclient.py" | grep -v "grep"`
if [ -z "${prc}" ]
then
	echo "Process is not running ${prc}:"
	export PYTHONPATH=$PYTHONPATH:/etc/paho.mqtt.python/build/lib/
	python mqttclient.py > /dev/null 2>&1 &
else
	echo "Process is running ${prc}"
fi
