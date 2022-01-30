"""
DSMR Dictionary:
dsmr version 5

index:
[description, mqtt_topic, regex received data, datatype, multiply factor, maxrate]]

INDEX = {
  "DESCRIPTION",
  "MQTT_TOPIC",
  "MQTT_TAG",
  "REGEX",
  "DATATYPE",
  "MULTIPLICATION",
  "MAXRATE"
}


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

DESCRIPTION = 0       # Description, specify units of measure between []
MQTT_TOPIC = 1        # MQTT base topic; will be packed in a json message
MQTT_TAG = 2          # MQTT tag in json message; Need to be unique per topic
REGEX = 3             # python regex to filter extract data from dsmr telegram
DATATYPE = 4          # data type of data (int, float, str)
MULTIPLICATION = 5    # In case of float of int, multiply factor (eg 1000 is unit is kW, and MQTT wants W)
MAXRATE = 6           # max nrof MQTT messages per hour (0: none; 1: 1 per hour; 3600: 1 per second IF smartmeter
                      # would generate more than 1 per second); assumption is that incoming messages are evenly
                      # spread in time
HA_DISCOVERY = 7      # 0 (False) or 1 (True)
HA_ICON = 8           # HA icons, check https://materialdesignicons.com/



# uncomment what is not being used
# MQTT_TOPIC is prefixed with MQTT_TOPIC_PREFIX (config.py)
definition = {
"1-3:0.2.8":    ["DSMR Version meter",            "system", "dsmr_version",     "^.*\((.*)\)",      "int", "1", "12",  "0"],

# set serial frequecy equal to el_consumed, then use it as as tag for influxdb; truncated to last 8 digits
# If full serial is required, remove \d{26}
"0-0:96.1.1":   ["Equipment identifier",          "el", "serial",              "^.*\(\d{26}(.*)\)","str",   "1",    "60", "0", "mdi:counter"],
"0-0:1.0.0":    ["Timestamp [s]",                 "el", "timestamp",           "^.*\((.*)W\)",     "int",   "1",    "0",   "0", "mdi:counter"],
"0-0:96.7.21":  ["Number of power failures",      "el", "power_failures",      "^.*\((.*)\)",      "int",   "1",    "12",  "0", "mdi:counter"],
"0-0:96.7.9":   ["Number of long power failures", "el", "long_power_failures", "^.*\((.*)\)",      "int",   "1",    "12",  "0", "mdi:counter"],
"0-0:96.14.0":  ["Tariff indicator electricity",  "el", "tariff_indicator",    "^.*\((.*)\)",      "int",   "1",    "0",   "0", "mdi:counter"],

"1-0:21.7.0":   ["Power usage L1 [W]",            "el", "P1_consumed",         "^.*\((.*)\*kW\)",  "float", "1000", "0",   "0", "mdi:gauge"],
"1-0:41.7.0":   ["Power usage L2 [W]",            "el", "P2_consumed",         "^.*\((.*)\*kW\)",  "float", "1000", "0",   "0", "mdi:gauge"],
"1-0:61.7.0":   ["Power usage L3 [W]",            "el", "P3_consumed",         "^.*\((.*)\*kW\)",  "float", "1000", "0",   "0", "mdi:gauge"],
"1-0:22.7.0":   ["Power generation L1 [W]",       "el", "P1_generated",        "^.*\((.*)\*kW\)",  "float", "1000", "0",   "0", "mdi:gauge"],
"1-0:42.7.0":   ["Power generation L2 [W]",       "el", "P2_generated",        "^.*\((.*)\*kW\)",  "float", "1000", "0",   "0", "mdi:gauge"],
"1-0:62.7.0":   ["Power generation L3 [W]",       "el", "P3_generated",        "^.*\((.*)\*kW\)",  "float", "1000", "0",   "0", "mdi:gauge"],
"1-0:1.7.0":    ["Total power usage [W]",         "el", "p_consumed",          "^.*\((.*)\*kW\)",  "float", "1000", "60", "1", "mdi:gauge"],
"1-0:2.7.0":    ["Total power generation [W]",    "el", "p_generated",         "^.*\((.*)\*kW\)",  "float", "1000", "60", "1", "mdi:gauge"],

# set serial frequency equal to gas_consumed, then use it as as tag for influxdb
# If full serial is required, remove \d{26}
"0-1:24.2.1":   ["gas consumption [m3]",          "gas", "gas_consumed",       "^.*\((.*)\*m3\)",  "float", "1000", "60", "1", "mdi:counter"],
"0-1:96.1.0":   ["Equipment Identifier",          "gas", "serial",             "^.*\(\d{26}(.*)\)","str",   "1",    "60", "0", "mdi:counter"],

"1-0:1.8.1":    ["EL consumed (Tariff 1) [Wh]",   "el", "el_consumed1",        "^.*\((.*)\*kWh\)", "float", "1000", "0", "0", "mdi:counter"],
"1-0:1.8.2":    ["EL consumed (Tariff 2) [Wh]",   "el", "el_consumed2",        "^.*\((.*)\*kWh\)", "float", "1000", "0", "0", "mdi:counter"],
"1-0:2.8.1":    ["EL returned (Tariff 1) [Wh]",   "el", "el_returned1",        "^.*\((.*)\*kWh\)", "float", "1000", "0", "0", "mdi:counter"],
"1-0:2.8.2":    ["EL returned (Tariff 2) [Wh]",   "el", "el_returned2",        "^.*\((.*)\*kWh\)", "float", "1000", "0", "0", "mdi:counter"],

# Virtual, not existing in dsmr telegram & specification, to sum tarif 1 & 2 to a single message
"1-0:1.8.3":    ["EL consumed [Wh]",              "el", "el_consumed",         "^.*\((.*)\*kWh\)", "float", "1000", "60", "1", "mdi:counter"],
"1-0:2.8.3":    ["EL returned [Wh]",              "el", "el_returned",         "^.*\((.*)\*kWh\)", "float", "1000", "60", "1", "mdi:counter"],

"1-0:32.7.0":   ["Voltage L1 [V]",                "el",     "V1",              "^.*\((.*)\*V\)",   "float", "1",    "60", "1", "mdi:gauge"],
"1-0:52.7.0":   ["Voltage L2 [V]",                "el",     "V2",              "^.*\((.*)\*V\)",   "float", "1",    "60", "1", "mdi:gauge"],
"1-0:72.7.0":   ["Voltage L3 [V]",                "el",     "V3",              "^.*\((.*)\*V\)",   "float", "1",    "60", "1", "mdi:gauge"],
"1-0:31.7.0":   ["Current L1 [A]",                "el",     "I1",              "^.*\((.*)\*A\)",   "int",   "1",    "0",   "0", "mdi:gauge"],
"1-0:51.7.0":   ["Current L2 [A]",                "el",     "I2",              "^.*\((.*)\*A\)",   "int",   "1",    "0",   "0", "mdi:gauge"],
"1-0:71.7.0":   ["Current L3 [A]",                "el",     "I3",              "^.*\((.*)\*A\)",   "int",   "1",    "0",   "0", "mdi:gauge"],

"1-0:32.36.0":  ["Voltage swells L1",             "el",     "V1_swells",       "^.*\((.*)\)",      "int",   "1",    "12",  "0", "mdi:gauge"],
"1-0:52.36.0":  ["Voltage swells L2",             "el",     "V2_swells",       "^.*\((.*)\)",      "int",   "1",    "12",  "0", "mdi:gauge"],
"1-0:72.36.0":  ["Voltage swells L3",             "el",     "V3_swells",       "^.*\((.*)\)",      "int",   "1",    "12",  "0", "mdi:gauge"],
"1-0:32.32.0":  ["Voltage sags L1",               "el",     "V1_sags",         "^.*\((.*)\)",      "int",   "1",    "12",  "0", "mdi:gauge"],
"1-0:52.32.0":  ["Voltage sags L2",               "el",     "V2_sags",         "^.*\((.*)\)",      "int",   "1",    "12",  "0", "mdi:gauge"],
"1-0:72.32.0":  ["Voltage sags L3",               "el",     "V3_sags",         "^.*\((.*)\)",      "int",   "1",    "12",  "0", "mdi:gauge"]

}

# Not supported:
#"0-1:24.1.0": ["Device-Type", "device_type", "^.*\((.*)\)", "int, ""1"],

#"1-0:99.97.0": ["Power Failure Event Log (long power failures)", "power_failure_event_log", "^.*\((.*)\)", "string"],
#"0-0:96.13.0": ["Text message max 1024 characters.", "text_message", "^.*\((.*)\)"],
