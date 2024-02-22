#!/usr/bin/python3

"""
 DESCRIPTION
   Read DSMR (Dutch Smart Meter Requirements) smart energy meter via P1 USB cable
   Tested on raspberry pi4

4 Worker threads:
  - P1 USB serial port reader
  - DSMR telegram parser to MQTT messages
  - MQTT client
  - HA Discovery

Only dsmr v50 is implemented; other versions can be supported by adapting dsmr50.py


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

__version__ = "4.0.0"
__author__  = "Hans IJntema"
__license__ = "GPLv3"

import signal
import socket
import time
import sys
import threading

# Local imports
import config as cfg
import P1_serial as p1
import P1_parser as convert
import hadiscovery as ha
import mqtt as mqtt

from log import logger
logger.setLevel(cfg.loglevel)

# DEFAULT exit code
# status=1/FAILURE
__exit_code = 1

# ------------------------------------------------------------------------------------
# Instance running?
# ------------------------------------------------------------------------------------
import os
script=os.path.basename(__file__)
script=os.path.splitext(script)[0]

# Ensure that only one instance is started
if sys.platform == "linux":
  lockfile = "\0" + script + "_lockfile"
  try:
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    # Create an abstract socket, by prefixing it with null.
    s.bind(lockfile)
    logger.info( f"Starting {__file__}; version = {__version__}" )
  except IOError as err:
    logger.info( f"{lockfile} already running. Exiting; {err}" )
    sys.exit(1)


def close():
  """
  Args:

  Returns:
    None
  """

  logger.info(f"Exitcode = {__exit_code} >>")
  sys.exit(__exit_code)


# ------------------------------------------------------------------------------------
# LATE GLOBALS
# ------------------------------------------------------------------------------------
trigger = threading.Event()
t_threads_stopper = threading.Event()
t_mqtt_stopper = threading.Event()

# mqtt thread
t_mqtt = mqtt.MQTTClient(mqtt_broker=cfg.MQTT_BROKER,
                         mqtt_port=cfg.MQTT_PORT,
                         mqtt_client_id=cfg.MQTT_CLIENT_UNIQ,
                         mqtt_qos=cfg.MQTT_QOS,
                         mqtt_cleansession=True,
                         mqtt_protocol=mqtt.MQTTv5,
                         username=cfg.MQTT_USERNAME,
                         password=cfg.MQTT_PASSWORD,
                         mqtt_stopper=t_mqtt_stopper,
                         worker_threads_stopper=t_threads_stopper)

# SerialPort thread
telegram = list()
t_serial = p1.TaskReadSerial(trigger, t_threads_stopper, telegram)

# Telegram parser thread
t_parse = convert.ParseTelegrams(trigger, t_threads_stopper, t_mqtt, telegram)

# Send Home Assistant auto discovery MQTT's
t_discovery = ha.Discovery(t_threads_stopper, t_mqtt, __version__)


def exit_gracefully(signal, stackframe):
  """
  Exit_gracefully

  Keyword arguments:
    :param int signal: the associated signalnumber
    :param str stackframe: current stack frame
    :return:
  """

  logger.debug(f"Signal {signal}: >>")

  # status=0/SUCCESS
  __exit_code = 0

  t_threads_stopper.set()
  logger.info("<<")


def main():
  logger.debug(">>")

  logger.info(f"P1 serial port = {cfg.ser_port}")
  logger.info(f"MQTT Max Rate = {cfg.MQTT_MAXRATE}")

  # Set last will/testament
  t_mqtt.will_set(cfg.MQTT_TOPIC_PREFIX + "/status", payload="offline", qos=cfg.MQTT_QOS, retain=True)

  # Start all threads
  t_mqtt.start()
  # Introduce a small delay before starting the parsing, otherwise initial messages cannot be published
  time.sleep(1)
  t_parse.start()
  t_discovery.start()
  t_serial.start()

  # Set status to online
  t_mqtt.set_status(cfg.MQTT_TOPIC_PREFIX + "/status", "online", retain=True)
  logger.debug(f'Meter status set to online')
  t_mqtt.do_publish(cfg.MQTT_TOPIC_PREFIX + "/sw-version", f"main={__version__}; mqtt={mqtt.__version__}", retain=True)

  # block till t_serial stops receiving telegrams/exits
  t_serial.join()
  logger.debug("t_serial.join exited; set stopper for other threats")
  t_threads_stopper.set()

  # Set status to offline
  t_mqtt.set_status(cfg.MQTT_TOPIC_PREFIX + "/status", "offline", retain=True)
  logger.debug(f'Meter status set to offline')

  # Todo check if MQTT queue is empty before setting stopper
  # Use a simple delay of 1sec before closing mqtt
  time.sleep(1)
  t_mqtt_stopper.set()

  logger.debug("<<" )
  return


# ------------------------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------------------------
if __name__ == '__main__':
  logger.debug("__main__: >>")
  signal.signal(signal.SIGINT, exit_gracefully)
  signal.signal(signal.SIGTERM, exit_gracefully)

  # start main program
  main()

  logger.debug("__main__: <<")
  close()
