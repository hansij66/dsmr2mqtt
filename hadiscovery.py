"""
  Send Home Assistant Auto Discovery MQTT messages


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

import time
import threading
import json
import re

# Local imports
import config as cfg
import dsmr50 as dsmr

# Logging
import __main__
import logging
import os
script = os.path.basename(__main__.__file__)
script = os.path.splitext(script)[0]
logger = logging.getLogger(script + "." + __name__)


class Discovery(threading.Thread):

  def __init__(self, stopper, mqtt, version):
    """
    class init

    Keyword arguments:
    :param threading.Event()    stopper:
    :param mqtt.mqttclient()    mqtt: reference to mqtt client
    :param str                  version: version of the program
    """

    logger.debug(">>")
    super().__init__()
    self.__stopper = stopper
    self.__mqtt = mqtt
    self.__version = version
    self.__interval = 3600/cfg.HA_INTERVAL
    self.__lastmqtt = 0
    self.__listofjsondicts = list()

  def __del__(self):
    logger.debug(">>")

  def __create_discovery_JSON(self):
    """
      Create the HA/MQTT Autodiscovery messages

    Returns:
      None
    """
    d = {}  # d = dict() does not work....

    # create device JSON
    d["name"] = "Status"
    d["unique_id"] = "dsmr-device"
    d["state_topic"] = cfg.MQTT_TOPIC_PREFIX + "/status"
    d["icon"] = "mdi:home-automation"
    d["device"] = {"name": "HA dsmr reader",
                   "sw_version": self.__version,
                   "model": "P1 USB/dsmr-mqtt",
                   "manufacturer": "hansij66 @github.com",
                   "identifiers": ["dsmr"]
                   }

    self.__listofjsondicts.append(d)

    # iterate through all dsmr.defintions
    for index in dsmr.definition:
      # select definitions with discovery enabled
      if int(dsmr.definition[index][dsmr.HA_DISCOVERY]):
        d = {}
        d["unique_id"] = dsmr.definition[index][dsmr.MQTT_TAG]
        d["state_topic"] = cfg.MQTT_TOPIC_PREFIX + "/" + dsmr.definition[index][dsmr.MQTT_TOPIC]
        d["name"] = dsmr.definition[index][dsmr.DESCRIPTION]
        d["unit_of_measurement"] = re.match(".*\[(\w+)\].*", dsmr.definition[index][dsmr.DESCRIPTION]).group(1)
        d["value_template"] = "{{value_json." + dsmr.definition[index][dsmr.MQTT_TAG] + "}}"

        # https://www.home-assistant.io/integrations/sensor/
        # https://developers.home-assistant.io/docs/core/entity/sensor/#long-term-statistics
        if d["unit_of_measurement"] == "Wh":
          d["device_class"] = "energy"
          d["state_class"] = "total"
        elif d["unit_of_measurement"] == "W":
          d["device_class"] = "power"
          #d["state_class"] = "measurement"
        elif d["unit_of_measurement"] == "A":
          d["device_class"] = "current"
        elif d["unit_of_measurement"] == "V":
          d["device_class"] = "voltage"
        elif d["unit_of_measurement"] == "m3" or d["unit_of_measurement"] == "m\u00b3":
          d["device_class"] = "gas"
          d["state_class"] = "total"

          # Homeassistant expects m3 and not liters
          d["value_template"] = "{{value_json." + dsmr.definition[index][dsmr.MQTT_TAG] + "|float/1000|round(0)" + "}}"
        else:
          logger.warning(f"Unknown unit_of_measurement = {d['unit_of_measurement']}")

        d["icon"] = dsmr.definition[index][dsmr.HA_ICON]
        d["device"] = { "identifiers": [ "dsmr" ] }

        self.__listofjsondicts.append(d)


  def run(self):
    """

    Returns:
      None
    """
    logger.debug(">>")

    self.__create_discovery_JSON()

    # infinite loop
    if cfg.HA_DISCOVERY:
      while not self.__stopper.is_set():
        # calculate time elapsed since last MQTT
        t_elapsed = int(time.time()) - self.__lastmqtt

        if t_elapsed > self.__interval:
          for dict in self.__listofjsondicts:
            topic = "homeassistant/sensor/" + cfg.MQTT_TOPIC_PREFIX + "/" + dict["unique_id"] + "/config"
            self.__mqtt.do_publish(topic, json.dumps(dict, separators=(',', ':')), retain=True)
            self.__lastmqtt = int(time.time())
        else:
          # wait...
          time.sleep(0.5)

    # If configured, remove MQTT Auto Discovery configuration
    if cfg.HA_DELETECONFIG:
      for dict in self.__listofjsondicts:
        topic = "homeassistant/sensor/" + cfg.MQTT_TOPIC_PREFIX + "/" + dict["unique_id"] + "/config"
        self.__mqtt.do_publish(topic, "")
