"""
  Rename to config.py

  Configure:
  - MQTT client
  - Home Assistant Discovery
  - USB P1 serial port
  - Debug level

  Configure the DSMR messages in dsmr50.py

"""

# [ LOGLEVELS ]
# DEBUG, INFO, WARNING, ERROR, CRITICAL
loglevel = "INFO"

# [ PRODUCTION ]
# True if run in production
# False when running in simulation
PRODUCTION = True

# File below is used when PRODUCTION is set to False
# Simulation file can be created in bash/Linux:
# tail -f /dev/ttyUSB0 > dsmr.raw (wait 10-15sec and hit ctrl-C)
# (assuming that P1 USB is connected as ttyUSB0)
# Add string "EOF" (without quotes) as last line
SIMULATORFILE = "test/dsmr.raw"

# [ MQTT Parameters ]
# Using local dns names is not always reliable with PAHO
MQTT_BROKER = "192.168.1.1"
MQTT_PORT = 1883
MQTT_CLIENT_UNIQ_ID = 'mqtt-dsmr'
MQTT_QOS = 1
MQTT_USERNAME = "username"
MQTT_PASSWORD = "***********"

# MAX number of MQTT messages per hour. Assumption is that incoming messages are evenly spread in time
# EXAMPLE 1: 1 per hour, 12: every 5min, 60: every 1min, 720; every 5sec, 3600: every 1sec
# Actual rate will never be higher than P1 dsmr messag rate
# MQTT_MAXRATE = [1..3600]
# MQTT_MAXRATE = 720
MQTT_MAXRATE = 60

if PRODUCTION:
  MQTT_TOPIC_PREFIX = "dsmr"
  MQTT_CLIENT_UNIQ = MQTT_CLIENT_UNIQ_ID
  HA_ID = ""
else:
  MQTT_TOPIC_PREFIX = "test_dsmr"
  MQTT_CLIENT_UNIQ = 'mqtt-dsmr-test'
  HA_ID = "TEST"

# [ Home Assistant ]
HA_DISCOVERY = True

# Default is False, removes the auto config message when this program exits
HA_DELETECONFIG = True

# Discovery messages per hour
# At start-up, always a discovery message is send
# Default is 12 ==> 1 message every 5 minutes. If the MQTT broker is restarted
# it can take up to 5 minutes before the dsmr device re-appears in HA
HA_DISCOVERY_RATE = 12

# [ P1 USB serial ]
# ser_port = "/dev/ttyUSB0"
ser_port = "/dev/tty-dsmr"
ser_baudrate = 115200
