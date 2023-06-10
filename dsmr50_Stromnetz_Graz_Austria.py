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
DATAVALIDATION = 5    # "0" (zero allowed), "1" (zero not allowed); check on data range; ignore if not valid; sometimes 0's recorded in influxdb
MULTIPLICATION = 6    # In case of float of int, multiply factor (eg 1000 is unit is kW, and MQTT wants W)
MAXRATE = 7           # max nrof MQTT messages per hour (0: none; 1: 1 per hour; 3600: 1 per second IF smartmeter
                      # would generate more than 1 per second); assumption is that incoming messages are evenly
                      # spread in time
HA_DISCOVERY = 8      # 0 (False) or 1 (True)
HA_ICON = 9           # HA icons, check https://materialdesignicons.com/

# MQTT_TOPIC is prefixed with MQTT_TOPIC_PREFIX (config.py)
definition = {
#                DESCRIPTION                    MTOPIC    MTAG                REGEX               Type     Val  Mult    MaxR   HA-D HA_icon
"1-3:0.2.8":    ["DSMR Version",          "system", "dsmr_version",     "^.*\((.*)\)",      "int",   "0", "1",    "12",  "0"               ],
"0-0:1.0.0":    ["Zeitstempel [s]",               "el",     "timestamp",        "^.*\((.*)S\)",     "int",   "1", "1",    "0",   "0", "mdi:counter"],

"1-0:1.8.0":    ["Wirkenergie Bezug [Wh]",            "el",     "el_consumed",      "^.*\((.*)\*Wh\)", "float", "1", "1", "60",  "1", "mdi:counter"],
"1-0:1.8.1":    ["Wirkenergie Bezug (Tarif 1) [Wh]",  "el",     "el_consumed1",     "^.*\((.*)\*Wh\)", "float", "1", "1", "0",   "0", "mdi:counter"],
"1-0:1.8.2":    ["Wirkenergie Bezug (Tarif 2) [Wh]",  "el",     "el_consumed2",     "^.*\((.*)\*Wh\)", "float", "1", "1", "0",   "0", "mdi:counter"],
"1-0:1.7.0":    ["Momentane Wirkleistung Bezug [W]",  "el",     "p_consumed",       "^.*\((.*)\*W\)",  "float", "0", "1", "60",  "1", "mdi:gauge"],

"1-0:2.8.0":    ["Wirkenergie Einspeisung [Wh]",            "el",     "el_returned",     "^.*\((.*)\*Wh\)", "float", "1", "1", "60", "1", "mdi:counter"],
"1-0:2.8.1":    ["Wirkenergie Einspeisung (Tarif 1) [Wh]",  "el",     "el_returned1",     "^.*\((.*)\*Wh\)", "float", "1", "1", "0", "0", "mdi:counter"],
"1-0:2.8.2":    ["Wirkenergie Einspeisung (Tarif 2) [Wh]",  "el",     "el_returned2",     "^.*\((.*)\*Wh\)", "float", "1", "1", "0", "0", "mdi:counter"],
"1-0:2.7.0":    ["Momentane Wirkleistung Einspeisung [W]",  "el",     "p_returned",      "^.*\((.*)\*W\)",  "float", "0", "1", "60", "1", "mdi:gauge"]
}


