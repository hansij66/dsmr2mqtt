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

    logger.debug(f'LOGGER: init class Discovery >>')
    super().__init__()
    self.__stopper = stopper
    self.__mqtt = mqtt
    self.__version = version
    self.__interval = 3600 / cfg.HA_DISCOVERY_RATE
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
    logger.debug(f'LOGGER: create device JSON')
    d["name"] = "status"
    d["unique_id"] = "dsmr-device" + cfg.HA_ID
    d["state_topic"] = cfg.MQTT_TOPIC_PREFIX + "/status"
    d["icon"] = "mdi:home-automation"
    d["device"] = {"name": "DSMR P1" + cfg.HA_ID,
                   "sw_version": self.__version,
                   "model": "P1 USB/dsmr-mqtt" + cfg.HA_ID,
                   "manufacturer": "https://github.com/hansij66/dsmr2mqtt",
                   "identifiers": ["dsmr" + cfg.HA_ID]
                   }

    self.__listofjsondicts.append(d)

    # iterate through all dsmr.defintions
    logger.debug(f'LOGGER: iterate through all dsmr.defintions')
    for index in dsmr.definition:
      # select definitions with discovery enabled
      if int(dsmr.definition[index][dsmr.HA_INCLUDED]):
        tag = str(dsmr.definition[index][dsmr.MQTT_TAG])
        description = str(dsmr.definition[index][dsmr.DESCRIPTION])
        regex = dsmr.definition[index][dsmr.REGEX]
        # Check if multiple MQTT_TAG and DESCRIPTION have been defined, semicolon separated
        tag_matches = re.split(";", tag)
        description_matches = re.split(";", description)

        # Create loop for telegram messages that will contain multiple values
        i = 0

        # Check if tag, description and regex contain equal amount of elements
        if len(tag_matches) == len(description_matches) == re.compile(regex).groups:
          while i < re.compile(regex).groups:
            d = {}
            d["unique_id"] = tag_matches[i]
            d["state_topic"] = cfg.MQTT_TOPIC_PREFIX + "/" + dsmr.definition[index][dsmr.MQTT_TOPIC]
            d["name"] = description_matches[i]

            if dsmr.definition[index][dsmr.UNIT] != "":
              d["unit_of_measurement"] = dsmr.definition[index][dsmr.UNIT]
            else:
              d["unit_of_measurement"] = ""

            d["value_template"] = "{{ value_json." + tag_matches[i] + " }}"

            # Define here all the units that are measured by the meter and that are
            # supported in HA as available device classes
            # https://developers.home-assistant.io/docs/core/entity/sensor/#available-device-classes
            # https://www.home-assistant.io/integrations/sensor/
            # https://developers.home-assistant.io/docs/core/entity/sensor/#long-term-statistics
            if d["unit_of_measurement"] == "Wh":
              d["device_class"] = "ENERGY"
              d["state_class"] = "total"
            elif d["unit_of_measurement"] == "W":
              d["device_class"] = "POWER"
#              d["state_class"] = "measurement"
            elif d["unit_of_measurement"] == "A":
              d["device_class"] = "CURRENT"
#              d["state_class"] = "measurement"
            elif d["unit_of_measurement"] == "V":
              d["device_class"] = "VOLTAGE"
#              d["state_class"] = "measurement"
            elif d["unit_of_measurement"] == "m3" or d["unit_of_measurement"] == "m\u00b3":
              d["device_class"] = "GAS"
              d["state_class"] = "total"

              # Homeassistant expects m3 and not liters
              d["value_template"] = "{{value_json." + tag_matches[i] + "|float/1000|round(0)" + "}}"
            else:
              logger.debug(f"Unknown unit_of_measurement = {d['unit_of_measurement']}")

            i += 1

            d["icon"] = dsmr.definition[index][dsmr.HA_ICON]
            d["device"] = {"identifiers": ["dsmr" + cfg.HA_ID]}

            # logger.debug(f'LOGGER: %s', d)
            logger.debug(
              f'LOGGER: sensor config created with unique_id = {d["unique_id"]} and description = {d["name"]}')

            self.__listofjsondicts.append(d)
        else:
          logger.warning(f'WARNING: entries in the DSMR50.py file do not contain equal amounts for tag = {tag}, regex = {regex} and description = {description}')

  def run(self):
    """

    Returns:
      None
    """
    logger.debug(">>")

    self.__create_discovery_JSON()

    # infinite loop
    if cfg.HA_DISCOVERY:
      logger.info(f'Home Assistant config discovery is enabled')
      while not self.__stopper.is_set():
        # calculate time elapsed since last MQTT
        t_elapsed = int(time.time()) - self.__lastmqtt

        if t_elapsed > self.__interval:
          for _dict in self.__listofjsondicts:
            topic = "homeassistant/sensor/" + cfg.MQTT_TOPIC_PREFIX + "/" + _dict["unique_id"] + "/config"
            self.__mqtt.do_publish(topic, json.dumps(_dict, separators=(',', ':')), retain=True)
            self.__lastmqtt = int(time.time())
        else:
          # wait...
          time.sleep(0.5)
    else:
      logger.info(f'Home Assistant config discovery is DISABLED')

    # If configured, remove MQTT Auto Discovery configuration
    if cfg.HA_DELETECONFIG:
      for _dict in self.__listofjsondicts:
        topic = "homeassistant/sensor/" + cfg.MQTT_TOPIC_PREFIX + "/" + _dict["unique_id"] + "/config"
        self.__mqtt.do_publish(topic, "")
