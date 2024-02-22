"""
  Parses P1 telegrams to MQTT messages
  Select MQTT messages based on dsmr50.py
  Queue MQTT messages

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

import threading
import copy
import re
import time
import json
import config as cfg
import dsmr50 as dsmr

# Logging
import __main__
import logging
import os
script = os.path.basename(__main__.__file__)
script = os.path.splitext(script)[0]
logger = logging.getLogger(script + "." + __name__)


class ParseTelegrams(threading.Thread):
  """
  """

  def __init__(self, trigger, stopper, mqtt, telegram):
    """
    Args:
      :param threading.Event() trigger: signals that new telegram is available
      :param threading.Event() stopper: stops thread
      :param mqtt.mqttclient() mqtt: reference to mqtt worker
      :param list() telegram: dsmr telegram
    """
    logger.debug(">>")
    super().__init__()
    self.__trigger = trigger
    self.__stopper = stopper
    self.__telegram = telegram
    self.__mqtt = mqtt
    self.__prev_ts = 0

    assert cfg.MQTT_MAXRATE > 0, "MQTT_MAXRATE outside range 1.3600"
    assert cfg.MQTT_MAXRATE <= 3600, "MQTT_MAXRATE outside range 1.3600"
    self.__min_ts_interval = int(3600 / cfg.MQTT_MAXRATE)

    # Count number of topics which will always be included in MQTT json
    # timestamp key:value topic
    self.__nroftopics = 1

    logger.debug(f"NROF = {self.__nroftopics}")

  def __del__(self):
    logger.debug(">>")

  def __publish_telegram(self, listofjsondicts):
    # publish the dictionaries per topic
    for d in listofjsondicts:
      topic = d["topic"]

      # remove topic key:value pair, otherwise it will be packed in the mqtt json
      d.pop("topic")

      # There is always a timestamp key:value and a database:influxdb in the dictionary (len = 2)
      # If there are no other key-value pairs, skip publishing to MQTT
      if len(d) > self.__nroftopics:
        topic = cfg.MQTT_TOPIC_PREFIX + "/" + topic

        # make resilient against double forward slashes in topic
        topic = topic.replace('//', '/')
        message = json.dumps(d, sort_keys=True, separators=(',', ':'))
        self.__mqtt.do_publish(topic, message, retain=False)
    return

  def __decode_telegram_element(self, index, element, ts, listofjsondicts):
    # logger.debug(f">> index={index};  element={element}")

    try:
      # Extract result from telegram element, based on dsmr definition
      # Cast result to type defined in dsmr50
      # .....this is normally "dangerous", as you can define any python function....but it is hardcoded
      # in dsmr50.py file, which should be read-only for regular users
      cast = dsmr.definition[index][dsmr.DATATYPE]
      dsmr_data = re.match(dsmr.definition[index][dsmr.REGEX], element).group(1)

      # multiplication factor for data, eg to convert kW to W
      multiply = dsmr.definition[index][dsmr.MULTIPLICATION]

      # dict & json pair
      # tag:data
      # If type is string, there is no multiplication factor
      if cast != "str":
        data = eval(cast)(dsmr_data) * eval(cast)(multiply)
      else:
        data = eval(cast)(dsmr_data)
        # logger.debug(f"CAST = {}")

      # dict & json pair
      # tag:data
      tag = str(dsmr.definition[index][dsmr.MQTT_TAG])

      # MQTT topic
      topic = str(dsmr.definition[index][dsmr.MQTT_TOPIC])

      # If topic does not exist yet, create & initialize dictionary for this topic;
      # Add tag:data pairs; which will be converted to mqtt json later on.
      # Add dictionary to list
      if not any(dictionary['topic'] == topic for dictionary in listofjsondicts):

        dict_element = {"topic": topic, "timestamp": ts}
        listofjsondicts.append(dict_element)

      for dictionary in listofjsondicts:
        if dictionary['topic'] == topic:
            dictionary[tag] = data

    except Exception as e:
      logger.debug(f"Exception {e}")
      pass

  def __decode_telegrams(self, telegram):
    """
    Args:
      :param list telegram:

    Returns:

    """
    logger.debug(f">>")

    # list of dictionaries of mqtt messages which will be converted to json format
    listofjsondicts = list()

    # epoch time stamp
    ts = int(time.time())

    # Calculate time in seconds between between previous mqtt transmission and current
    # If time between previous mqtt message and now is large enough, send
    # mqtt message and store current timestamp
    if (ts - self.__prev_ts) > self.__min_ts_interval:
      self.__prev_ts = ts

      for element in telegram:
        try:
          # Extract the identifier (eg "1-0:1.8.1") of the element
          # and use this as index for dsmr.definition
          index = re.match(r"(\d{0,3}-\d{0,3}:\d{0,3}\.\d{0,3}\.\d{0,3}).*", element).group(1)
          self.__decode_telegram_element(index, element, ts, listofjsondicts)

        except Exception as e:
          logger.debug(f"Exception {e}")
          # To handle empty lines or lines not matching dsmr definitions (checksum, header, empty line)
          pass

      logger.debug(f"DICT = {listofjsondicts}")

      self.__publish_telegram(listofjsondicts)
    else:
      logger.debug(f"Telegram is skipped; time elapsed since last MQTT message = {(ts - self.__prev_ts)}")
    return

  def run(self):
    logger.debug(">>")

    while not self.__stopper.is_set():
      # block till event is set, but implement timeout to allow stopper
      self.__trigger.wait(timeout=1)
      if self.__trigger.is_set():
        # Make copy of the telegram, for further parsing
        telegram = copy.deepcopy(self.__telegram)

        # Clear telegram list for next capture by ReadSerial class
        self.__telegram.clear()

        # Clear trigger, serial can continue
        self.__trigger.clear()

        self.__decode_telegrams(telegram)

    logger.debug("<<")
