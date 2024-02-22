"""
DSMR Dictionary: version 5

Use this table to define the OBIS codes that have to be parsed from the meter and published to the MQTT broker

See below at definition of constants for further explanations.

Configuration:
OBIS code + all 9 fields must be present in the definition for the data to be parsed properly

OBISCODE: [
  DESCRIPTION,
  MQTT_TOPIC,
  MQTT_TAG,
  REGEX,
  UNIT,
  DATATYPE,
  MULTIPLICATION,
  HA_HA_INCLUDED,
  HA_ICON
  ]

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# CONSTANTS - DON'T CHANGE
# Used as index for dsmr message definition list

# Description (appears in HA as sensor names)
DESCRIPTION = 0

# MQTT base topic; will be packed in a json message
# In this example: <system, el, gas>
MQTT_TOPIC = 1

# MQTT tag in json message
# Needs to be unique per topic
MQTT_TAG = 2

# Python regex to filter extract data from dsmr telegram
# Test with: https://regex101.com/
REGEX = 3

# Unit of the measurement according to what HA expects
# Allowed values: <W, Wh, kW, kWh, V, A, m3>
UNIT = 4

# data type of data
# Allowed values: <int, float, str>
# Keep in mind that only measurements should have value datatype int or float
# Other info should be parsed as str
DATATYPE = 5

# In case of float of int, multiply factor (eg 1000 is unit is kW, and MQTT wants W)
# Allowed values: number
MULTIPLICATION = 6

# Include this OBIS data element in Home Assistant Auto Discovery
# Allowed values: 0 (False) or 1 (True)
HA_INCLUDED = 7

# HA icons, check https://materialdesignicons.com/
HA_ICON = 8

# A typical MQTT message:
# test_dsmr
#   status = online
#   sw-version = main=4.0.0; mqtt=2.0.0
#   system = {"dsmr_version":"50","timestamp":1708459993}
#   el = {"P1_consumed":716.0,"P1_generated":0.0,"P2_consumed":55.0,"P2_generated":0.0,"P3_consumed":117.0,
#         "P3_generated":0.0,"V1":232.0,"V1_sags":5,"V1_swells":0,"V2":232.0,"V2_sags":5,"V2_swells":0,"V3":232.0,
#         "V3_sags":4,"V3_swells":0,"el_consumed":23679687.0,"el_consumed1":16230145.0,"el_consumed2":7449542.0,
#         "el_returned":21097674.0,"el_returned1":5998736.0,"el_returned2":15098938.0,"long_power_failures":12,
#         "p_consumed":889.0,"p_generated":0.0,"power_failures":1373,"serial":"33363137","tariff_indicator":1,
#         "timestamp":1708542164}
#   gas = {"gas_consumed":10142194.0,"serial":"33313137","timestamp":1708542182}


# Comment what is not being used
# MQTT_TOPIC is prefixed with MQTT_TOPIC_PREFIX (config.py)

# "OBIS Reference" : [DSMR definition]
# "0-0:96.1.1":   ["Equipment identifier",....]

definition = {
"1-3:0.2.8":
   ["DSMR Version meter", "system", "dsmr_version", "^.*\((.*)\)",
   "", "str", "1", "0", "mdi:counter"],

# Serial/equipment identifier is truncated to last 8 digits and used as tag in influxdb
# If full serial is required, remove \d{26} or change to \d{34}
"0-0:96.1.1":
  ["Equipment identifier", "el", "serial", "^.*\(\d{26}(.*)\)",
   "", "str", "1", "0", "mdi:tag-text-outline"],

"0-0:96.1.4":
  ["Version information", "el", "version", "^.*\((.*)\)", "",
   "str", "1", "0", "mdi:numeric"],

"0-0:96.7.21":
  ["Number power failures", "el", "power_failures", "^.*\((.*)\)",
   "", "int", "1", "1", "mdi:transmission-tower-off"],

"0-0:96.7.9":
  ["Number long power failures", "el", "long_power_failures", "^.*\((.*)\)",
   "", "int", "1", "1", "mdi:transmission-tower-off"],

"0-0:96.14.0":
  ["Tariff indicator electricity", "el", "tariff_indicator", "^.*\((.*)\)",
  "", "int", "1", "1", "mdi:weather-night"],

"1-0:21.7.0":
  ["Power usage L1", "el", "P1_consumed", "^.*\((.*)\*kW\)",
   "W", "float", "1000", "1", "mdi:gauge"],

"1-0:41.7.0":
  ["Power usage L2", "el", "P2_consumed", "^.*\((.*)\*kW\)",
   "W", "float", "1000", "1", "mdi:gauge"],

"1-0:61.7.0":
  ["Power usage L3", "el", "P3_consumed", "^.*\((.*)\*kW\)",
   "W", "float", "1000", "1", "mdi:gauge"],

"1-0:22.7.0":
  ["Power generation L1", "el", "P1_generated", "^.*\((.*)\*kW\)",
   "W", "float", "1000", "1", "mdi:gauge"],

"1-0:42.7.0":
  ["Power generation L2", "el", "P2_generated", "^.*\((.*)\*kW\)",
   "W", "float", "1000", "1", "mdi:gauge"],

"1-0:62.7.0":
  ["Power generation L3", "el", "P3_generated", "^.*\((.*)\*kW\)",
   "W", "float", "1000", "1", "mdi:gauge"],

"1-0:1.7.0":
  ["Total power usage", "el", "p_consumed", "^.*\((.*)\*kW\)",
  "W", "float", "1000", "1", "mdi:gauge"],

"1-0:2.7.0":
  ["Total power generation", "el", "p_generated", "^.*\((.*)\*kW\)",
  "W", "float", "1000", "1", "mdi:gauge"],

# Serial/equipment identifier is truncated to last 8 digits and used as tag in influxdb
# If full serial is required, remove \d{26} or change to \d{34}
"0-1:24.2.1":
  ["Gas consumption", "gas", "gas_consumed", "^.*\((.*)\*m3\)",
   "m\u00b3", "float", "1000", "1", "mdi:counter"],

"0-1:96.1.0":
  ["Equipment Identifier", "gas", "serial", "^.*\(\d{26}(.*)\)",
   "", "str", "1", "0", "mdi:tag-text-outline"],

"1-0:1.8.1":
  ["EL consumed (Tariff 1)", "el", "el_consumed1", "^.*\((.*)\*kWh\)",
   "Wh", "float", "1000", "1", "mdi:counter"],

"1-0:1.8.2":
  ["EL consumed (Tariff 2)", "el", "el_consumed2", "^.*\((.*)\*kWh\)",
   "Wh", "float", "1000", "1", "mdi:counter"],

"1-0:2.8.1":
  ["EL returned (Tariff 1)", "el", "el_returned1", "^.*\((.*)\*kWh\)",
   "Wh", "float", "1000", "1", "mdi:counter"],

"1-0:2.8.2":
  ["EL returned (Tariff 2)", "el", "el_returned2", "^.*\((.*)\*kWh\)",
   "Wh", "float", "1000", "1", "mdi:counter"],

# Virtual, not existing in dsmr telegram & specification, to sum tarif 1 & 2 to a single message
"1-0:1.8.3":
  ["EL consumed", "el", "el_consumed", "^.*\((.*)\*kWh\)",
   "Wh", "float", "1000", "1", "mdi:counter"],

"1-0:2.8.3":
  ["EL returned", "el", "el_returned", "^.*\((.*)\*kWh\)",
   "Wh", "float", "1000", "1", "mdi:counter"],

"1-0:32.7.0":
  ["Voltage L1", "el", "V1", "^.*\((.*)\*V\)",
  "V", "float", "1", "1", "mdi:gauge"],

"1-0:52.7.0":
  ["Voltage L2", "el", "V2", "^.*\((.*)\*V\)",
  "V", "float", "1", "1", "mdi:gauge"],

"1-0:72.7.0":
  ["Voltage L3", "el", "V3", "^.*\((.*)\*V\)",
  "V", "float", "1", "1", "mdi:gauge"],

# Current seems to be measured in whole integer numbers (1, 2, 3....); if you need accurate current
# numbers, you better divide Power by Volt to get a more accurate numer
#"1-0:31.7.0":
#  ["Current L1", "el", "I1", "^.*\((.*)\*A\)",
#  "A", "int", "1", "1", "mdi:gauge"],

#"1-0:51.7.0":
#  ["Current L2", "el", "I2", "^.*\((.*)\*A\)",
#  "A", "int", "1", "0", "mdi:gauge"],

#"1-0:71.7.0":
#  ["Current L3", "el", "I3", "^.*\((.*)\*A\)",
#  "A", "int", "1", "0", "mdi:gauge"],

"1-0:32.36.0":
  ["Voltage swells L1", "el", "V1_swells", "^.*\((.*)\)",
  "", "int", "1", "1", "mdi:elevation-rise"],

"1-0:52.36.0":
  ["Voltage swells L2", "el", "V2_swells", "^.*\((.*)\)",
  "", "int", "1", "1", "mdi:elevation-rise"],

"1-0:72.36.0":
  ["Voltage swells L3", "el", "V3_swells", "^.*\((.*)\)",
  "", "int", "1", "1", "mdi:elevation-rise"],

"1-0:32.32.0":
  ["Voltage sags L1", "el", "V1_sags", "^.*\((.*)\)",
  "", "int", "1", "1", "mdi:elevation-decline"],

"1-0:52.32.0":
  ["Voltage sags L2", "el", "V2_sags", "^.*\((.*)\)",
  "", "int", "1", "1", "mdi:elevation-decline"],

"1-0:72.32.0":
  ["Voltage sags L3", "el", "V3_sags", "^.*\((.*)\)",
  "", "int", "1", "1", "mdi:elevation-decline"],

#"0-0:96.3.10":
#  ["Breaker state", "el", "breaker", "^.*\((.*)\)",
#  "", "int", "1", "1", "mdi:electric-switch"],

#"0-0:17.0.0":
#  ["Limiter threshold", "el", "limiter", "^.*\((.*)\*kW\)",
#  "W", "float", "1000", "1", "mdi:speedometer"],

#"1-0:31.4.0":
#  ["Fuse supervision threshold L1", "el", "fuse", "^.*\((.*)\*A\)",
#  "A", "int", "1", "1", "mdi:gauge"],

#"0-0:96.13.0":
#  ["Text message", "el", "text", "^.*\((.*)\)",
#  "", "str", "1", "1", "mdi:text"],

#"1-0:1.4.0":
#  ["Current average demand", "el", "avg_dem", "^.*\((.*)\*kW\)",
#  "W", "float", "1000", "1", "mdi:gauge"]

}

# Not supported:
#"0-1:24.1.0": ["Device-Type", "device_type", "^.*\((.*)\)", "int, ""1"],

#"1-0:99.97.0": ["Power Failure Event Log (long power failures)", "power_failure_event_log", "^.*\((.*)\)", "string"],
#"0-0:96.13.0": ["Text message max 1024 characters.", "text_message", "^.*\((.*)\)"],

#"1-0:1.6.0":
#  ["Monthly peak timestamp;Monthly peak DST;Monthly peak value", "el", "m_peak_ts;m_peak_dst;m_peak_val", "^.*\((\d{12})(S|W)\)\((.*)\*kW\)",
#  "", "int;str;float", "0", "1", "1", "mdi:chart-bar"],

#"0-0:98.1.0":
#  ["Historical peaks", "el", "h_peak", "^.*\((\d{12})(S|W)\)\((\d{12})(S|W)\)\((.*)\*kW\)\((\d{12})(S|W)\)\((\d{12})(S|W)\)\((.*)\*kW\)\((\d{12})(S|W)\)\((\d{12})(S|W)\)\((.*)\*kW\)\((\d{12})(S|W)\)\((\d{12})(S|W)\)\((.*)\*kW\)\((\d{12})(S|W)\)\((\d{12})(S|W)\)\((.*)\*kW\)\((\d{12})(S|W)\)\((\d{12})(S|W)\)\((.*)\*kW\)\((\d{12})(S|W)\)\((\d{12})(S|W)\)\((.*)\*kW\)\((\d{12})(S|W)\)\((\d{12})(S|W)\)\((.*)\*kW\)\((\d{12})(S|W)\)\((\d{12})(S|W)\)\((.*)\*kW\)",
#  "", "int", "1", "1", "mdi:chart-bar"],


# NOT USED; An EPOCH timestamp is added every MQTT message
# ["Timestamp [s]", "el", "timestamp", "^.*\((\d{12})(S|W)\)", "",
#"0-0:1.0.0":
#  ["Timestamp [s]", "el", "timestamp", "^.*\((.*)W\)",
#   "s", "int", "1", "1", "1", "mdi:clock-time-four"],