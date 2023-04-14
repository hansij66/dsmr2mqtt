"""
 DESCRIPTION

 REQUIRED:
   Include this module only in top level main module:
====================================================================
from log import logger
import logging

# This setLevel determines wich messages are passed on to lower handlers
logger.setLevel(logging.DEBUG)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
====================================================================


   In other modules, include snippet below:

====================================================================
import __main__
import logging
import os
script=os.path.basename(__main__.__file__)
script=os.path.splitext(script)[0]
logger = logging.getLogger(script + "." +  __name__)
====================================================================
V1.2.0
  11-4-2023
  Restructering directory; __init__.py; no code change

V1.1.0
  31-10-2021
  Disable syslog handler for non linux platforms

V0.1:
- initial version

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


# ------------------------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------------------------
import __main__
import logging
from logging.handlers import SysLogHandler
import os
import sys
import getpass


currentuser = getpass.getuser()

script = os.path.basename(__main__.__file__)
script = os.path.splitext(script)[0]

logger = logging.getLogger(script)

# This setLevel determines which messages are passed on to lower handlers
logger.setLevel(logging.INFO)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
logger.propagate = False

# Console stdout
c_handler = logging.StreamHandler(sys.stdout)
# This setLevel determines wich messages are processed by this handler (assuming it arrives from global logger)
c_handler.setLevel(logging.DEBUG)
c_format = logging.Formatter('%(name)s %(levelname)s: FUNCTION:%(funcName)s LINE:%(lineno)d: %(message)s')
c_handler.setFormatter(c_format)
logger.addHandler(c_handler)

# Syslog
if sys.platform == "linux":
  s_handler = logging.handlers.SysLogHandler(address='/dev/log')
  # This setLevel determines which messages are processed by this handler (assuming it arrives from global logger)
  s_handler.setLevel(logging.INFO)
  s_format = logging.Formatter('%(name)s[%(process)d] %(levelname)s: '
                               '%(asctime)s FUNCTION:%(funcName)s LINE:%(lineno)d: %(message)s',
                               datefmt='%H:%M:%S')
  s_handler.setFormatter(s_format)
  logger.addHandler(s_handler)


# File
# Test if /dev/shm is writable otherwise use /tmp
try:
  if os.access("/dev/shm", os.W_OK):
    f_handler = logging.FileHandler(f"/dev/shm/{script}.{currentuser}.log", 'a')
  else:
    f_handler = logging.FileHandler(f"/tmp/{script}.{currentuser}.log", 'a')

  f_handler.setLevel(logging.ERROR)
  f_format = logging.Formatter('%(name)s[%(process)d] %(levelname)s: '
                               '%(asctime)s FUNCTION:%(funcName)s LINE:%(lineno)d: %(message)s',
                               datefmt='%Y-%m-%d,%H:%M:%S')
  f_handler.setFormatter(f_format)
  logger.addHandler(f_handler)
except Exception as e:
  print(f"Exception {e}: /dev/shm/{script}.log permission denied")

# logger.debug('This is a debug message')
# logger.info('This is an info message')
# logger.warning('This is a warning message')
# logger.error('This is an error message')
# logger.critical('This is a critical message')
# logger.exception("Exception occurred")
