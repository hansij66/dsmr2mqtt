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

# See the spec for the available OBIS codes: https://www.netbeheernederland.nl/_upload/Files/Slimme_meter_15_a727fce1f1.pdf

DESCRIPTION = 0       # Description, specify units of measure between []
MQTT_TOPIC = 1        # MQTT base topic; will be packed in a json message
MQTT_TAG = 2          # MQTT tag in json message; Need to be unique per topic
REGEX = 3             # python regex to filter extract data from dsmr telegram
DATATYPE = 4          # data type of data (int, float, str)
DATAVALIDATION = 5    # "0" (zero allowed), "1" (zero not allowed); check on data range; ignore if not valid; sometimes 0's recorded in influxdb
MULTIPLICATION = 6    # In case of float of int, multiply factor (eg 1000 is unit is kW, and MQTT wants W)
MAXRATE = 7           # max nrof MQTT messages per hour (0: none; 1: 1 per hour; 3600: 1 per second IF smartmeter
                      # would generate more than 1 per second); assumption is that incoming messages are evenly
                      # spread in time
HA_DISCOVERY = 8      # 0 (False) or 1 (True)
HA_ICON = 9           # HA icons, check https://materialdesignicons.com/


# Uncomment what is not being used
# MQTT_TOPIC is prefixed with MQTT_TOPIC_PREFIX (config.py)
definition = {
"1-3:0.2.8":    ["DSMR Version meter",                     "system",   "dsmr_version",          "^.*\((.*)\)",      "int",   "0", "1",    "12",  "1"],

# set serial frequecy equal to elec_consumed, then use it as as tag for influxdb; truncated to last 8 digits
# If full serial is required, remove \d{26}
"0-0:96.1.1":   ["Equipment identifier",                   "elec",     "serial",                "^.*\(\d{26}(.*)\)","str",   "1", "1",    "60",  "1", "mdi:counter"],
"0-0:1.0.0":    ["Timestamp [s]",                          "elec",     "timestamp",             "^.*\((.*)W\)",     "int",   "1", "1",    "0",   "1", "mdi:counter"],
"0-0:96.7.21":  ["Number of power failures",               "elec",     "power_failures",        "^.*\((.*)\)",      "int",   "0", "1",    "12",  "1", "mdi:counter"],
"0-0:96.7.9":   ["Number of long power failures",          "elec",     "long_power_failures",   "^.*\((.*)\)",      "int",   "0", "1",    "12",  "1", "mdi:counter"],
"0-0:96.14.0":  ["Tariff indicator electricity",           "elec",     "tariff_indicator",      "^.*\((.*)\)",      "int",   "0", "1",    "0",   "1", "mdi:counter"],

"1-0:21.7.0":   ["Power consumption L1 [W]",               "elec",     "P_L1_consumed",         "^.*\((.*)\*kW\)",  "float", "0", "1000", "60",  "0", "mdi:gauge"],
"1-0:41.7.0":   ["Power consumption L2 [W]",               "elec",     "P_L2_consumed",         "^.*\((.*)\*kW\)",  "float", "0", "1000", "60",  "0", "mdi:gauge"],
"1-0:61.7.0":   ["Power consumption L3 [W]",               "elec",     "P_L3_consumed",         "^.*\((.*)\*kW\)",  "float", "0", "1000", "60",  "0", "mdi:gauge"],
"1-0:22.7.0":   ["Power production L1 [W]",                "elec",     "P_L1_produced",         "^.*\((.*)\*kW\)",  "float", "0", "1000", "60",  "0", "mdi:gauge"],
"1-0:42.7.0":   ["Power production L2 [W]",                "elec",     "P_L2_produced",         "^.*\((.*)\*kW\)",  "float", "0", "1000", "60",  "0", "mdi:gauge"],
"1-0:62.7.0":   ["Power production L3 [W]",                "elec",     "P_L3_produced",         "^.*\((.*)\*kW\)",  "float", "0", "1000", "60",  "0", "mdi:gauge"],
"1-0:1.7.0":    ["Total power consumption [W]",            "elec",     "P_consumed",            "^.*\((.*)\*kW\)",  "float", "0", "1000", "60",  "1", "mdi:gauge"],
"1-0:2.7.0":    ["Total power production [W]",             "elec",     "P_produced",            "^.*\((.*)\*kW\)",  "float", "0", "1000", "60",  "1", "mdi:gauge"],

# set serial frequency equal to gas_consumed, then use it as as tag for influxdb
# If full serial is required, remove \d{26}
"0-1:24.2.1":   ["Gas consumption [m\u00b3]",              "gas",      "gas_consumed",          "^.*\((.*)\*m3\)",  "float", "1", "1000", "60",  "1", "mdi:counter"],
"0-1:96.1.0":   ["Equipment Identifier",                   "gas",      "serial",                "^.*\(\d{26}(.*)\)","str",   "1", "1",    "60",  "0", "mdi:counter"],

"1-0:1.8.1":    ["Electricity consumed (Tariff 1) [Wh]",   "elec",     "elec_consumed_tar1",    "^.*\((.*)\*kWh\)", "float", "1", "1000", "0",   "0", "mdi:counter"],
"1-0:1.8.2":    ["Electricity consumed (Tariff 2) [Wh]",   "elec",     "elec_consumed_tar2",    "^.*\((.*)\*kWh\)", "float", "1", "1000", "0",   "0", "mdi:counter"],
"1-0:2.8.1":    ["Electricity produced (Tariff 1) [Wh]",   "elec",     "elec_produced_tar1",    "^.*\((.*)\*kWh\)", "float", "1", "1000", "0",   "0", "mdi:counter"],
"1-0:2.8.2":    ["Electricity produced (Tariff 2) [Wh]",   "elec",     "elec_produced_tar2",    "^.*\((.*)\*kWh\)", "float", "1", "1000", "0",   "0", "mdi:counter"],

# Virtual, not existing in dsmr telegram & specification, to sum tarif 1 & 2 to a single message
"1-0:1.8.3":    ["Electricity consumed [Wh]",              "elec",     "elec_consumed",         "^.*\((.*)\*kWh\)", "float", "1", "1000", "60",  "1", "mdi:counter"],
"1-0:2.8.3":    ["Electricity produced [Wh]",              "elec",     "elec_produced",         "^.*\((.*)\*kWh\)", "float", "1", "1000", "60",  "1", "mdi:counter"],

"1-0:32.7.0":   ["Voltage L1 [V]",                         "elec",     "V_L1",                  "^.*\((.*)\*V\)",   "float", "0", "1",    "60",  "1", "mdi:gauge"],
"1-0:52.7.0":   ["Voltage L2 [V]",                         "elec",     "V_L2",                  "^.*\((.*)\*V\)",   "float", "0", "1",    "60",  "1", "mdi:gauge"],
"1-0:72.7.0":   ["Voltage L3 [V]",                         "elec",     "V_L3",                  "^.*\((.*)\*V\)",   "float", "0", "1",    "60",  "1", "mdi:gauge"],
"1-0:31.7.0":   ["Current L1 [A]",                         "elec",     "I_L1",                  "^.*\((.*)\*A\)",   "int",   "0", "1",    "0",   "0", "mdi:gauge"],
"1-0:51.7.0":   ["Current L2 [A]",                         "elec",     "I_L2",                  "^.*\((.*)\*A\)",   "int",   "0", "1",    "0",   "0", "mdi:gauge"],
"1-0:71.7.0":   ["Current L3 [A]",                         "elec",     "I_L3",                  "^.*\((.*)\*A\)",   "int",   "0", "1",    "0",   "0", "mdi:gauge"],

"1-0:32.36.0":  ["Voltage swells L1",                      "elec",     "V_L1_swells",           "^.*\((.*)\)",      "int",   "0", "1",    "12",  "0", "mdi:gauge"],
"1-0:52.36.0":  ["Voltage swells L2",                      "elec",     "V_L2_swells",           "^.*\((.*)\)",      "int",   "0", "1",    "12",  "0", "mdi:gauge"],
"1-0:72.36.0":  ["Voltage swells L3",                      "elec",     "V_L3_swells",           "^.*\((.*)\)",      "int",   "0", "1",    "12",  "0", "mdi:gauge"],
"1-0:32.32.0":  ["Voltage sags L1",                        "elec",     "V_L1_sags",             "^.*\((.*)\)",      "int",   "0", "1",    "12",  "0", "mdi:gauge"],
"1-0:52.32.0":  ["Voltage sags L2",                        "elec",     "V_L2_sags",             "^.*\((.*)\)",      "int",   "0", "1",    "12",  "0", "mdi:gauge"],
"1-0:72.32.0":  ["Voltage sags L3",                        "elec",     "V_L3_sags",             "^.*\((.*)\)",      "int",   "0", "1",    "12",  "0", "mdi:gauge"]
}

# Not supported:
#"0-1:24.1.0": ["Device-Type", "device_type", "^.*\((.*)\)", "int, ""1"],

#"1-0:99.97.0": ["Power Failure Event Log (long power failures)", "power_failure_event_log", "^.*\((.*)\)", "string"],
#"0-0:96.13.0": ["Text message max 1024 characters.", "text_message", "^.*\((.*)\)"],
