"""
Read dsmr telgrams from P1 USB serial.


To test in bash the P1 usb connector:
raw -echo < /dev/ttyUSB0; cat -vt /dev/ttyUSB0

OR
sudo apt-get install -y python3-serial
sudo chmod o+rw /dev/ttyUSB0
python3 -m serial.tools.miniterm /dev/ttyUSB0 115200 --xonxoff



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

import serial
import threading
import time
import re

import config as cfg

# Logging
import __main__
import logging
import os
script = os.path.basename(__main__.__file__)
script = os.path.splitext(script)[0]
logger = logging.getLogger(script + "." + __name__)


class TaskReadSerial(threading.Thread):

  def __init__(self, trigger, stopper, telegram):
    """

    Args:
      :param threading.Event() trigger: signals that new telegram is available
      :param threading.Event() stopper: stops thread
      :param list() telegram: dsmr telegram
    """

    logger.debug(">>")
    super().__init__()
    self.__trigger = trigger
    self.__stopper = stopper
    self.__telegram = telegram
    self.__counter = 0

    # [ Serial parameters ]
    if cfg.PRODUCTION:
      self.__tty = serial.Serial()
      self.__tty.port = cfg.ser_port
      self.__tty.baudrate = cfg.ser_baudrate
      self.__tty.bytesize = serial.SEVENBITS
      self.__tty.parity = serial.PARITY_EVEN
      self.__tty.stopbits = serial.STOPBITS_ONE
      self.__tty.xonxoff = 0
      self.__tty.rtscts = 0
      self.__tty.timeout = 20
      logger.info(f"Using USB device {self.__tty.port} with baud {self.__tty.baudrate}")

    try:
      if cfg.PRODUCTION:
        self.__tty.open()
        logger.debug(f"serial {self.__tty.port} opened")
      else:
        self.__tty = open(cfg.SIMULATORFILE, 'rb')

    except Exception as e:
      logger.error(f"ReadSerial: {type(e).__name__}: {str(e)}")
      self.__stopper.set()
      raise ValueError('Cannot open P1 serial port', cfg.ser_port)

  def __del__(self):
    logger.debug(">>")

  def __preprocess(self):
    """
      Add a virtual dsmr entry, which is sum of tariff 1 and tariff 2

      "1-0:1.8.1" + "1-0:1.8.2" --> "1-0:1.8.3"
      "1-0:2.8.1" + "1-0:2.8.2" --> "1-0:2.8.3"

      1-0:1.8.1(016230.132*kWh)
      1-0:1.8.2(007449.542*kWh)
      1-0:2.8.1(005998.736*kWh)
      1-0:2.8.2(015098.938*kWh)

    Returns:
      None
    """

    e_consumed = 0.0
    e_returned = 0.0

    for element in self.__telegram:
      try:
        value = re.match(r"1-0:1\.8\.1\((\d{6}\.\d{3})\*kWh\)", element).group(1)
        e_consumed = e_consumed + float(value)
      except AttributeError:
        pass

      try:
        value = re.match(r"1-0:1\.8\.2\((\d{6}\.\d{3})\*kWh\)", element).group(1)
        e_consumed = e_consumed + float(value)
      except AttributeError:
        pass

      try:
        value = re.match(r"1-0:2\.8\.1\((\d{6}\.\d{3})\*kWh\)", element).group(1)
        e_returned = e_returned + float(value)
      except AttributeError:
        pass

      try:
        value = re.match(r"1-0:2\.8\.2\((\d{6}\.\d{3})\*kWh\)", element).group(1)
        e_returned = e_returned + float(value)
      except AttributeError:
        pass

    # Insert the virtual entries in the dsmr telegram
    e_consumed = "{0:10.3f}".format(e_consumed)
    line = f"1-0:1.8.3({e_consumed}*kWh)"
    self.__telegram.append(line)

    e_returned = "{0:10.3f}".format(e_returned)
    line = f"1-0:2.8.3({e_returned}*kWh)"
    self.__telegram.append(line)

  def __read_serial(self):
    """
      Opens & Closes serial port
      Reads dsmr telegrams; stores in global variable (self.__telegram)
      Sets threading event to signal other clients (parser) that
      new telegram is available.
      In non-production mode, reads telegrams from file

    Returns:
      None
    """
    logger.debug(">>")

    while not self.__stopper.is_set():

      # wait till parser has copied telegram content
      # ...we need the opposite of trigger.wait()...block when set; not available
      while self.__trigger.is_set():
        time.sleep(0.1)

      # add a counter as first field to the list
      self.__counter += 1
      self.__telegram.append(f"{self.__counter}")

      # Decode from binary to ascii
      # Remove CR LF
      line = self.__tty.readline().decode('utf-8').rstrip()

      # First element in telegram starts with "!"
      nrof_elements = 0
      while (not self.__stopper.is_set()) and (not line.startswith('!')):
        self.__telegram.append(line)
        line = self.__tty.readline().decode('utf-8').rstrip()
        nrof_elements += 1
#        logger.debug(f"TELEGRAM Element = {line}")

        # Only in simulator mode; detect EOF in file
        if (not cfg.PRODUCTION) and line.startswith('EOF'):
          self.__stopper.set()
          logger.debug(f"EOF Detected in {cfg.SIMULATORFILE}")
          break

      # do some magic on telegram
      self.__preprocess()

      # Trigger that new telegram is available for MQTT
      self.__trigger.set()

      # In simulation mode, insert a delay
      if not cfg.PRODUCTION:
        # 1sec delay mimics dsmr behaviour, which transmits every 1sec a telegram
        time.sleep(1.0)

    logger.debug("<<")

  def run(self):
    logger.debug(">>")
    try:
      # In production, ReadSerial has infinite loop
      # In simulation, ReadSerial will return @ EOF
      self.__read_serial()

    except Exception as e:
      logger.error(f"Exception: {e}")

    finally:
      self.__tty.close()
      self.__stopper.set()

    logger.debug("<<")
