# homeautomation
Various scripts for home automation

* databasewatchdog.py: Watchdog script that checks that the last database entry is younger than a certain time
* mqttclient.py: script that listens to mqtt stream and writes json data poins to database
* runmqttclient.sh: script that runs mqttclient.py if not already running

```
*/10	*	*	*	*	root	/etc/runmqttclient.sh > /root/log_runmqttclient.txt 2>&1
17	17	*	*	*	root	python /etc/databasewatchdog.py > /root/log_databasewatchdog.txt 2>&1
```
