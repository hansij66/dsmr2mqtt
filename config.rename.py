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

# Max nrof MQTT messages per second
# Set to 0 for unlimited rate
MQTT_RATE = 100

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

# [ InfluxDB ]
# Add a influxdb database tag, for Telegraf processing (database:INFLUXDB)
# This is not required for core functionality of this parser
# Set to None if Telegraf is not used
INFLUXDB = "dsmr"
#INFLUXDB = None

"""
influx
use dsmr
select * from dsmr
name: dsmr
time                V1  V1_sags V1_swells V2  V2_sags V2_swells V3  V3_sags V3_swells el_consumed el_returned gas_consumed long_power_failures p_consumed p_generated power_failures serial   topic
----                --  ------- --------- --  ------- --------- --  ------- --------- ----------- ----------- ------------ ------------------- ---------- ----------- -------------- ------   -----
1642192185000000000                                                                                           10142194                                                               33313137 dsmr/gas
1642192185000000000 231 5       0         234 5       0         233 4       0         23679674    21097674                 12                  866        0           1373           33363137 dsmr/el


# telegraf.conf
# Configuration for influxdb server to send metrics to
[[outputs.influxdb]]
  urls = ["http://influxdb:8086"]
  database = "telegraf" # required

  ## The value of this tag will be used to determine the database.  If this
  database_tag = "database"

  ## If true, the 'database_tag' will not be included in the written metric.
  exclude_database_tag = true

  ## Retention policy to write to. Empty string writes to the default rp.
  retention_policy = ""

  ## Write consistency (clusters only), can be: "any", "one", "quorum", "all"
  write_consistency = "any"

  ## Write timeout (for the InfluxDB client), formatted as a string.
  ## If not provided, will default to 5s. 0s means no timeout (not recommended).
  timeout = "5s"


# https://github.com/influxdata/telegraf/blob/release-1.14/plugins/inputs/mqtt_consumer/README.md
[[inputs.mqtt_consumer]]
  servers = ["tcp://mqtt:1883"]
  username = "ijntema"
  password = "mosquitto0000"
  qos = 0
  topics = [ "dsmr/el", "dsmr/gas" ]
  client_id = "telegraf-dsmr"

  # uncomment if topic tag has to be excluded.
  # Can only be done if all fields are unique
  # across all topics
#  tagexclude = [ "topic" ]

  # https://github.com/influxdata/telegraf/tree/master/plugins/parsers/json_v2
  # gjson playground: https://gjson.dev/
  data_format = "json_v2"
  [[inputs.mqtt_consumer.json_v2]]

    # A string that will become the new measurement name
    measurement_name = "dsmr"

    # A string with valid GJSON path syntax to a valid timestamp (single value)
    timestamp_path = "@this.timestamp"
    timestamp_format = "unix"

    [[inputs.mqtt_consumer.json_v2.object]]
      # A string with valid GJSON path syntax, can include array's and object's
      path = "@this"

      ### Configuration to define what JSON keys should be included and how (field/tag) ###
      # List of JSON keys (for a nested key, prepend the parent keys with underscores) to be a tag instead of a field,
      # when adding a JSON key in this list you don't have to define it in the included_keys list
      # database tag to determine which influxdb to be used
      tags = ["database", "serial"]

      # List of JSON keys (for a nested key, prepend the parent keys with underscores) that shouldn't be included in result
      # Exclude the mqtt/json key "timestamp" from influxdb
      excluded_keys = ["timestamp"]

      # A map of JSON keys (for a nested key, prepend the parent keys with underscores) with a type (int,uint,float,string,bool)
      [inputs.mqtt_consumer.json_v2.object.fields]
        V1 = "uint"
        V2 = "uint"
        V3 = "uint"
        V1_sags = "uint"
        V2_sags = "uint"
        V3_sags = "uint"
        V1_swells = "uint"
        V2_swells = "uint"
        V3_swells = "uint"
        el_consumed = "uint"
        el_returned = "uint"
        p_consumed = "uint"
        p_generated = "uint"
        long_power_failures = "uint"
        power_failures = "uint"
        timestamp = "uint"
        gas_consumed = "uint"
        database = "string"

"""
