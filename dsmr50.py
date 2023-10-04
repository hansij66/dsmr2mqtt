"""
DSMR Dictionary: version 5 - Fluvius

Use this table to define the OBIS codes that have to be parsed from the meter and publised to the MQTT broker

Please change the MAXRATE and HA_DISCOVERY fields accordingly to allow data to be published
HA_DISCOVERY = 1 but MAXRATE = 0 will still result in no meter data to be published
If you do not want HA_DISCOVERY (and configure your sensors in configuration.yaml) for certain meter data,
but only data to be sent, set HA_DISCOVERY = 0 and MAXRATE > 0.
To completely disable HA_DISCOVERY, set HA_DISCOVERY = False in config.py

Configuration:
OBIS code + all fields (11) must be present as a line in the definition for the data to be parsed properly

index: [
  DESCRIPTION,
  MQTT_TOPIC,
  MQTT_TAG,
  REGEX,
  UNIT,
  DATATYPE,
  DATAVALIDATION,
  MULTIPLICATION,
  MAXRATE,
  HA_DISCOVERY,
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

# See the spec for the available OBIS codes: https://www.netbeheernederland.nl/_upload/Files/Slimme_meter_15_a727fce1f1.pdf

DESCRIPTION = 0       # Description, specify units of measure between []
MQTT_TOPIC = 1        # MQTT base topic; will be packed in a json message
MQTT_TAG = 2          # MQTT tag in json message; Need to be unique per topic
REGEX = 3             # python regex to filter extract data from dsmr telegram
                      # Test with: https://regex101.com/
UNIT = 4              # Unit of the measurement according to what HA expects
                      # "0" (zero allowed), "1" (zero not allowed)
DATATYPE = 5          # data type of data
                      # Allowed values: int, float, str
                      # Keep in mind that only measurements should have value datatype int or float
                      # Other info should be parsed as str
DATAVALIDATION = 6    # Check on data range; ignore if not valid; sometimes 0's recorded in influxdb
                      # "0" (zero allowed), "1" (zero not allowed)
MULTIPLICATION = 7    # In case of float of int, multiply factor (eg 1000 is unit is kW, and MQTT wants W)
                      # Allowed values: number
MAXRATE = 8           # max number of MQTT messages per hour. Assumption is that incoming messages are evenly spread in time
                      # Allowed values: 0: none, 1: 1 per hour, 12: every 5min, 60: every 1min, 720; every 5sec, 3600: every 1sec
                      # (if smartmeter would generate more than 1 per second);
HA_DISCOVERY = 9      # This will publish the config to HA, but MAXRATE different than 0 will allow meter data publication
                      # Allowed values: 0 (False) or 1 (True)
HA_ICON = 10          # HA icons, check https://materialdesignicons.com/

# Define here all the units that are measured by the meter and that are supported in HA as available device classes
# See: https://developers.home-assistant.io/docs/core/entity/sensor/#available-device-classes
ha_supported_units = ["kWh", "kW", "A", "V", "m3", "m\u00b3"]

# MQTT_TOPIC is prefixed with MQTT_TOPIC_PREFIX (config.py)
# Comment what is not being used

#               DESCRIPTION                                      MQTT_TOPIC  MQTT_TAG                 REGEX                      UNIT   DT       DV   MP      MAXR    HA_DISCOVERY
definition = {
"1-3:0.2.8":    ["Version information for P1 output",            "system",   "dsmr_version",          "^.*\((.*)\)",             "",    "str",   "0", "1",    "12",  "1", "mdi:counter"],

"0-0:96.1.4":   ["Version information",                          "elec",     "version_information",   "^.*\((.*)\)",             "",    "str",   "1", "1",    "60",  "1", "mdi:counter"],
"0-0:96.1.1":   ["Equipment identifier",                         "elec",     "serial",                "^.*\((\d{28})",             "",    "str",   "1", "1",    "60",  "1", "mdi:counter"],
"0-0:1.0.0":    ["Timestamp [s]",                                "elec",     "timestamp",             "^.*\((\d{12})(S|W)\)",    "",    "int",   "1", "1",    "60",  "1", "mdi:counter"],
"0-0:96.7.21.255": ["Number of power failures in any phases",      "elec",   "power_failures",        "^.*\((.*)\)",             "",    "str",   "0", "1",    "60",  "1", "mdi:counter"],
"0-0:96.7.9.255":  ["Number of long power failures in any phases", "elec",   "long_power_failures",   "^.*\((.*)\)",             "",    "str",   "0", "1",    "60",  "1", "mdi:counter"],
"0-0:96.14.0":  ["Tariff indicator electricity",                 "elec",     "tariff_indicator",      "^.*\((.*)\)",             "",    "str",   "0", "1",    "60",  "1", "mdi:counter"],

"1-0:21.7.0":   ["Instantaneous active power L1 +P",             "elec",     "P_L1_consumed",         "^.*\((.*)\*kW\)",         "kW",  "float", "0", "1", "60",  "1", "mdi:gauge"],
"1-0:41.7.0":   ["Instantaneous active power L2 +P",             "elec",     "P_L2_consumed",         "^.*\((.*)\*kW\)",         "kW",  "float", "0", "1", "60",  "0", "mdi:gauge"],
"1-0:61.7.0":   ["Instantaneous active power L3 +P",             "elec",     "P_L3_consumed",         "^.*\((.*)\*kW\)",         "kW",  "float", "0", "1", "60",  "0", "mdi:gauge"],
"1-0:22.7.0":   ["Instantaneous active power L1 -P",             "elec",     "P_L1_produced",         "^.*\((.*)\*kW\)",         "kW",  "float", "0", "1", "60",  "1", "mdi:gauge"],
"1-0:42.7.0":   ["Instantaneous active power L2 -P",             "elec",     "P_L2_produced",         "^.*\((.*)\*kW\)",         "kW",  "float", "0", "1", "60",  "0", "mdi:gauge"],
"1-0:62.7.0":   ["Instantaneous active power L3 -P",             "elec",     "P_L3_produced",         "^.*\((.*)\*kW\)",         "kW",  "float", "0", "1", "60",  "0", "mdi:gauge"],
"1-0:1.7.0":    ["Actual electricity power delivered +P",        "elec",     "P_consumed",            "^.*\((.*)\*kW\)",         "kW",  "float", "0", "1", "60",  "1", "mdi:gauge"],
"1-0:2.7.0":    ["Actual electricity power received -P",         "elec",     "P_produced",            "^.*\((.*)\*kW\)",         "kW",  "float", "0", "1", "60",  "1", "mdi:gauge"],

"0-1:24.2.1":   ["Gas consumption [m\u00b3]",                    "gas",      "gas_consumed",          "^.*\((.*)\*m3\)",         "kW",  "float", "1", "1000", "60",  "0", "mdi:counter"],
"0-1:96.1.0":   ["Equipment Identifier",                         "gas",      "serial",                "^.*\(\d{26}(.*)\)",       "",    "str",   "1", "1",    "60",  "0", "mdi:counter"],

"1-0:1.8.1":    ["Electricity consumed (Tariff 1)",              "elec",     "elec_consumed_tar1",    "^.*\((.*)\*kWh\)",        "kWh", "float", "1", "1", "60",   "1", "mdi:counter"],
"1-0:1.8.2":    ["Electricity consumed (Tariff 2)",              "elec",     "elec_consumed_tar2",    "^.*\((.*)\*kWh\)",        "kWh", "float", "1", "1", "60",   "1", "mdi:counter"],
"1-0:2.8.1":    ["Electricity produced (Tariff 1)",              "elec",     "elec_produced_tar1",    "^.*\((.*)\*kWh\)",        "kWh", "float", "1", "1", "60",   "1", "mdi:counter"],
"1-0:2.8.2":    ["Electricity produced (Tariff 2)",              "elec",     "elec_produced_tar2",    "^.*\((.*)\*kWh\)",        "kWh", "float", "1", "1", "60",   "1", "mdi:counter"],

# Virtual, not existing in dsmr telegram & specification, to sum tarif 1 & 2 to a single message
"1-0:1.8.3":    ["Electricity consumed",                         "elec",     "elec_consumed",         "^.*\((.*)\*kWh\)",        "kWh", "float", "1", "1", "60",  "1", "mdi:counter"],
"1-0:2.8.3":    ["Electricity produced",                         "elec",     "elec_produced",         "^.*\((.*)\*kWh\)",        "kWh", "float", "1", "1", "60",  "1", "mdi:counter"],

"1-0:32.7.0":   ["Instantaneous voltage L1",                     "elec",     "V_L1",                  "^.*\((.*)\*V\)",          "V",   "float", "0", "1",    "60",  "1", "mdi:gauge"],
"1-0:52.7.0":   ["Instantaneous voltage L2",                     "elec",     "V_L2",                  "^.*\((.*)\*V\)",          "V",   "float", "0", "1",    "60",  "0", "mdi:gauge"],
"1-0:72.7.0":   ["Instantaneous voltage L3",                     "elec",     "V_L3",                  "^.*\((.*)\*V\)",          "V",   "float", "0", "1",    "60",  "0", "mdi:gauge"],
"1-0:31.7.0":   ["Instantaneous current L1",                     "elec",     "I_L1",                  "^.*\((.*)\*A\)",          "A",   "float", "0", "1",    "60",  "1", "mdi:gauge"],
"1-0:51.7.0":   ["Instantaneous current L2",                     "elec",     "I_L2",                  "^.*\((.*)\*A\)",          "A",   "float", "0", "1",    "60",  "0", "mdi:gauge"],
"1-0:71.7.0":   ["Instantaneous current L3",                     "elec",     "I_L3",                  "^.*\((.*)\*A\)",          "A",   "float", "0", "1",    "60",  "0", "mdi:gauge"],

"1-0:32.36.0":  ["Number of voltage swells L1",                  "elec",     "V_L1_swells",           "^.*\((.*)\)",             "",    "str",   "0", "1",    "60",  "1", "mdi:gauge"],
"1-0:52.36.0":  ["Number of voltage swells L2",                  "elec",     "V_L2_swells",           "^.*\((.*)\)",             "",    "str",   "0", "1",    "60",  "0", "mdi:gauge"],
"1-0:72.36.0":  ["Number of voltage swells L3",                  "elec",     "V_L3_swells",           "^.*\((.*)\)",             "",    "str",   "0", "1",    "60",  "0", "mdi:gauge"],
"1-0:32.32.0":  ["Number of voltage sags L1",                    "elec",     "V_L1_sags",             "^.*\((.*)\)",             "",    "str",   "0", "1",    "60",  "1", "mdi:gauge"],
"1-0:52.32.0":  ["Number of voltage sags L2",                    "elec",     "V_L2_sags",             "^.*\((.*)\)",             "",    "str",   "0", "1",    "60",  "0", "mdi:gauge"],
"1-0:72.32.0":  ["Number of voltage sags L3",                    "elec",     "V_L3_sags",             "^.*\((.*)\)",             "",    "str",   "0", "1",    "60",  "0", "mdi:gauge"],

"0-0:96.3.10":  ["Breaker state",                                "elec",     "breaker_state",         "^.*\((.*)\)",             "",    "str",   "0", "1",    "60",  "1", "mdi:gauge"],
"0-0:17.0.0":   ["Limiter threshold",                            "elec",     "limiter_threshold",     "^.*\((.*)\*kW\)",         "",    "float", "0", "1",    "60",  "1", "mdi:gauge"],
"1-0:31.4.0":   ["Fuse supervision threshold L1",                "elec",     "fuse_threshold",        "^.*\((.*)\*A\)",          "",    "float", "0", "1",    "60",  "1", "mdi:gauge"],
"0-0:96.13.0":  ["Text message",                                 "elec",     "text_message",          "^.*\((.*)\)",             "",    "str",   "0", "1",    "60",  "1", "mdi:gauge"],

"1-0:1.6.0":    ["Monthly peak",                                 "elec",     "monthly_peak",          "^.*\((\d{12})(S|W)\)\((.*)\*kW\)",   "",    "str",   "0", "1",    "60",  "1", "mdi:gauge"],
#"0-0:98.1.0":    ["Historical peaks",                                 "elec",     "historical_peaks",          "^.*\((.*)S\)\((.*)\*kW\)",   "",    "int",   "0", "1",    "12",  "1", "mdi:gauge"],
"1-0:1.4.0":    ["Current average demand",                       "elec",     "average_demand",        "^.*\((.*)\*kW\)",         "",    "float", "0", "1",    "60",  "1", "mdi:gauge"]
}


#0-0:98.1.0(9)(1-0:1.6.0)(1-0:1.6.0)(230101000000W)(221218090000W)(04.813*kW)(230201000000W)(230123133000W)(04.325*kW)(230301000000W)(230212183000W)(04.659*kW)(230401000000S)(230310133000W)(04.067*kW)(230501000000S)(230401131500S)(03.131*kW)(230601000000S)(230515133000S)(03.418*kW)(230701000000S)(230630144500S)(03.642*kW)(230801000000S)(230706130000S)(02.415*kW)(230901000000S)(230809190000S)(03.263*kW)
#^.*\((\d{12})(S|W)\)\((\d{12})(S|W)\)\((.*)\*kW\)\((\d{12})(S|W)\)\((\d{12})(S|W)\)\((.*)\*kW\)\((\d{12})(S|W)\)\((\d{12})(S|W)\)\((.*)\*kW\)\((\d{12})(S|W)\)\((\d{12})(S|W)\)\((.*)\*kW\)\((\d{12})(S|W)\)\((\d{12})(S|W)\)\((.*)\*kW\)\((\d{12})(S|W)\)\((\d{12})(S|W)\)\((.*)\*kW\)\((\d{12})(S|W)\)\((\d{12})(S|W)\)\((.*)\*kW\)\((\d{12})(S|W)\)\((\d{12})(S|W)\)\((.*)\*kW\)\((\d{12})(S|W)\)\((\d{12})(S|W)\)\((.*)\*kW\)