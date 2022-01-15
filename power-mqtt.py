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

V1.0.0:
  - Initial version


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

__version__ = "1.0.0"
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


def Close(exit_code):
  """
  Args:
    :param int exit_code: 0 success; 1 error

  Returns:
    None
  """

  logger.info(f"INFO:Close: exitcode = {exit_code} >>")
  sys.exit(exit_code)


# ------------------------------------------------------------------------------------
# LATE GLOBALS
# ------------------------------------------------------------------------------------
trigger = threading.Event()
threads_stopper = threading.Event()
mqtt_stopper = threading.Event()

# mqtt thread
t_mqtt = mqtt.mqttclient(cfg.MQTT_BROKER,
                         cfg.MQTT_PORT,
                         cfg.MQTT_CLIENT_UNIQ,
                         cfg.MQTT_RATE,
                         cfg.MQTT_QOS,
                         cfg.MQTT_USERNAME,
                         cfg.MQTT_PASSWORD,
                         mqtt_stopper,
                         threads_stopper)

# SerialPort thread
telegram = list()
t_serial = p1.TaskReadSerial(trigger, threads_stopper, telegram)

# Telegram parser thread
t_parse = convert.ParseTelegrams(trigger, threads_stopper, t_mqtt, telegram)

# Send Home Assistant auto discovery MQTT's
t_discovery = ha.Discovery(threads_stopper, t_mqtt, __version__)


def exit_gracefully(signal, stackframe):
  """
  Exit_gracefully

  Keyword arguments:
    :param int signal: the associated signalnumber
    :param str stackframe: current stack frame
    :return:
  """

  logger.debug(f"Signal {signal}: >>")

  threads_stopper.set()

  # allow all loops to finish
  logger.debug(f"wait 1 sec to shutdown everything else")
  time.sleep(1)
  logger.info("<<")


def main():
  logger.debug(">>")

  # Start all threads
  t_mqtt.start()
  t_parse.start()
  t_discovery.start()
  t_serial.start()

  # Set status to online
  t_mqtt.do_publish(cfg.MQTT_TOPIC_PREFIX + "/status", "online", retain=True)

  # block till t_serial stops receiving telegrams/exits
  t_serial.join()
  logger.debug("t_serial.join exited; set stopper for other threats")
  threads_stopper.set()

  # Set status to offline
  t_mqtt.do_publish(cfg.MQTT_TOPIC_PREFIX + "/status", "offline", retain=True)

  # Todo check if MQTT queue is empty before setting stopper
  # Use a simple delay of 1sec before closing mqtt
  time.sleep(1)
  mqtt_stopper.set()

  logger.debug("<<" )
  return


# ------------------------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------------------------
if __name__ == '__main__':
  logger.debug("__main__: >>")
  signal.signal(signal.SIGINT, exit_gracefully)

  # start main program
  main()

  logger.debug("__main__: <<")
  Close(0)
