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
# Using local dns names was not always reliable with PAHO
MQTT_BROKER = "192.168.1.1"
MQTT_PORT = 1883
MQTT_CLIENT_UNIQ = 'mqtt-dsmr'
MQTT_QOS = 1
MQTT_USERNAME = "username"
MQTT_PASSWORD = "secret"

if PRODUCTION:
  MQTT_TOPIC_PREFIX = "dsmr"
else:
  MQTT_TOPIC_PREFIX = "test_dsmr"

# [ Home Assistant ]
HA_DISCOVERY = True

# Default is False, removes the auto config message when this program exits
HA_DELETECONFIG = False

# Discovery messages per hour
# At start-up, always a discovery message is send
# Default is 12 ==> 1 message every 5 minutes. If the MQTT broker is restarted
# it can take up to 5 minutes before the dsmr device re-appears in HA
HA_INTERVAL = 12

# [ P1 USB serial ]
ser_port = "/dev/ttyUSB0"
ser_baudrate = 115200
