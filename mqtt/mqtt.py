"""
  MQTT class using paho-mqtt

  https://github.com/eclipse/paho.mqtt.python/blob/master/src/paho/mqtt/client.py
  https://www.eclipse.org/paho/index.php?page=clients/python/index.php
  http://www.steves-internet-guide.com/mqtt-clean-sessions-example/
  http://www.steves-internet-guide.com/python-mqtt-client-changes/
  http://www.steves-internet-guide.com/mqttv5/
  https://www.hivemq.com/blog/mqtt5-essentials-part6-user-properties/
  https://cedalo.com/blog/configuring-paho-mqtt-python-client-with-examples/

  v1.0.0: initial version
  v1.0.1: add last will
  V1.1.0: 31-7-2022: Add subscribing to MQTT server
  v1.1.3: on_disconnect rc=1 (out of memory) stop program
  v1.1.4: Add test for subscribing; whether message queue is set
  V1.1.5: Fix MQTT_ERR_NOMEM
  v1.1.6: Add clean session
  v2.0.0: Parameterize clean session; remove mqtt-rate

  LIMITATIONS
  * Only transport = TCP supported; websockets is not supported
  * Clean_session and clean-start partially implemented (not relevant for publishing clients)

  Class ReasonCodes:
  MQTT version 5.0 reason codes class.
  See ReasonCodes Names for a list of possible numeric values along with their
  names and the packets to which they apply.


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
import random
import string
import socket
import paho.mqtt.client as mqtt_client
import paho.mqtt as paho_mqtt
from pkg_resources import parse_version

# Logging
import __main__
import logging
import os
script = os.path.basename(__main__.__file__)
script = os.path.splitext(script)[0]
logger = logging.getLogger(script + "." + __name__)

# TODO
# MQTT_ERR_NOMEM is not very accurate; is often similar to MQTT_ERR_CONN_LOST
# eg stopping Mosquitto server generates a MQTT_ERR_NOMEM
# However, there are cases that client freezes for ethernity after a MQTT_ERR_NOMEM
# Implement a recover? With timeout? Try to reconnect?


class MQTTClient(threading.Thread):
  def __init__(self,
               mqtt_broker,
               mqtt_stopper,
               mqtt_port=1883,
               mqtt_client_id=None,
               mqtt_qos=1,
               mqtt_cleansession=True,
               mqtt_protocol=mqtt_client.MQTTv311,
               username="",
               password="",
               worker_threads_stopper=None):

    """
    Args:
      :param str mqtt_broker: ip or dns
      :param threading.Event() mqtt_stopper: indicate to stop the mqtt thread; typically as last thread
      in main loop to flush out all mqtt messages
      :param int mqtt_port:
      :param str mqtt_client_id:
      :param int mqtt_qos: MQTT QoS 0,1,2 for publish
      :param bool mqtt_cleansession:
      :param int mqtt_protocol: MQTT protocol version
      :param str username:
      :param str password:
      :param threading.Event() worker_threads_stopper: stopper event for other worker threads;
      typically the worker threads are
             stopped in the main loop before the mqtt thread;but mqtt thread can also set this in case of failure

    Returns:
      None
    """

    logger.info(f">> paho-mqtt version = {paho_mqtt.__version__}")
    super().__init__()

    self.__mqtt_broker = mqtt_broker
    self.__mqtt_stopper = mqtt_stopper
    self.__mqtt_port = mqtt_port

    # Generate random client id if not specified;
    # Basename ('script', from log module) and extended with 10 random characters
    if mqtt_client_id is None:
      self.__mqtt_client_id = script + '_' + ''.join(random.choice(string.ascii_lowercase) for _i in range(10))
    else:
      self.__mqtt_client_id = mqtt_client_id

    logger.info(f"MQTT Client ID = {self.__mqtt_client_id}")

    self.__qos = mqtt_qos
    self.__mqtt_cleansession = mqtt_cleansession
    self.__mqtt_protocol = mqtt_protocol

    if worker_threads_stopper is None:
      self.__worker_threads_stopper = self.__mqtt_stopper
    else:
      self.__worker_threads_stopper = worker_threads_stopper

    # Check if installed paho-mqtt version supports MQTT v5
    # Demote to v311 if wrong version is installed
    if self.__mqtt_protocol == mqtt_client.MQTTv5:
      if parse_version(f"{paho_mqtt.__version__}") < parse_version("1.5.1"):
        logger.warning(f"Incorrect paho-mqtt version ({paho_mqtt.__version__}) to support MQTT v5, "
                       f"reverting to MQTT v311")
        self.__mqtt_protocol = mqtt_client.MQTTv311

    # clean_session is only implemented for MQTT v3
    if self.__mqtt_protocol == mqtt_client.MQTTv311 or self.__mqtt_protocol == mqtt_client.MQTTv31:
      self.__mqtt = mqtt_client.Client(self.__mqtt_client_id,
                                       clean_session=mqtt_cleansession,
                                       protocol=self.__mqtt_protocol)
    elif self.__mqtt_protocol == mqtt_client.MQTTv5:
      self.__mqtt = mqtt_client.Client(self.__mqtt_client_id,
                                       protocol=self.__mqtt_protocol)
    else:
      logger.error(f"Unknown MQTT protocol version {mqtt_protocol}....exit")
      self.__worker_threads_stopper.set()
      self.__mqtt_stopper.set()
      return

    # Indicate whether thread has started - run() has been called
    self.__run = False

    # Todo parameterize
    self.__keepalive = 600

    # MQTT client tries to force a reconnection if
    # Client remains disconnected for more than MQTT_CONNECTION_TIMEOUT seconds
    self.__MQTT_CONNECTION_TIMEOUT = 60

    # Call back functions
    self.__mqtt.on_connect = self.__on_connect
    self.__mqtt.on_disconnect = self.__on_disconnect
    self.__mqtt.on_message = self.__on_message

    # Uncomment if needed for debugging
#    self.__mqtt.on_publish = self.__on_publish
#    self.__mqtt.on_log = self.__on_log

    if self.__mqtt_protocol == mqtt_client.MQTTv311 or self.__mqtt_protocol == mqtt_client.MQTTv31:
      self.__mqtt.on_subscribe = self.__on_subscribe_v31
    elif self.__mqtt_protocol == mqtt_client.MQTTv5:
      self.__mqtt.on_subscribe = self.__on_subscribe_v5
    else:
      self.__mqtt.on_subscribe = None

    self.__mqtt.on_unsubscribe = self.__on_unsubscribe

    # Not yet implemented
    # self.__mqtt.on_unsubscribe = self.__on_unsubscribe

    # Managed via __set_connected_flag()
    # Keeps track of connected status
    self.__connected_flag = False

    # Keep track how long client is disconnected
    # When threshold is exceeded, try to recover
    # In some cases, a MQTT_ERR_NOMEM is not recovered automatically
    self.__disconnect_start_time = int(time.time())

    # Maintain a mqtt message count
    self.__mqtt_counter = 0

    self.__mqtt.username_pw_set(username, password)

    # status topic & message
    self.__status_topic = None
    self.__status_payload = None
    self.__status_retain = None

    #######
    # Trigger to clients/threads to indicate that message is received and stored in queue
    self.__message_trigger = None

    # Queue to store received subscribed messages
    self.__subscribed_queue = None

    # list of subscribed topics
    self.__list_of_subscribed_topics = []

  def __del__(self):
    logger.debug(f">>")
    logger.info(f"Shutting down MQTT Client... {self.__mqtt_counter} MQTT messages have been published")

  def __internet_on(self):
    """
      Test if there is connectivity with the MQTT broker

    Returns:
      return: connectivity status (True, False)
      rtype: bool
    """
    logger.debug(f">>")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
      # Format: s.connect((HOST, PORT))
      s.connect((f"{self.__mqtt_broker}", int(self.__mqtt_port)))
      s.shutdown(socket.SHUT_RDWR)
      logger.debug(f"Internet connectivity to MQTT broker {self.__mqtt_broker} at port {self.__mqtt_port} available")
      return True
    except Exception as e:
      logger.info(f"Internet connectivity to MQTT broker {self.__mqtt_broker} at port {self.__mqtt_port} "
                  f"NOT yet available; Exception {e}")
      return False

  def __set_connected_flag(self, flag=True):
    logger.debug(f">> flag={flag}; current __connected_flag={self.__connected_flag}")

    # if flag == False and __connected_flag == True; start trigger
    if not flag and self.__connected_flag:
      self.__disconnect_start_time = int(time.time())
      logger.debug("Disconnect TIMER started")

    self.__connected_flag = flag
    return

  def __on_connect(self, _client, userdata, flags, rc, _properties=None):
    """
    Callback: when the client receives a CONNACK response from the broker.

    Args:
      :param ? _client: the client instance for this callback
      :param ? userdata: the private user data as set in Client()
      :param dict flags: response flags sent by the broker
      :param int rc: the connection result --> connack_dict
      :param _properties: The MQTT v5.0 properties received from the broker.  A
              list of Properties class instances.

    Returns:
      None
    """
    logger.debug(f">>")
    if rc == mqtt_client.CONNACK_ACCEPTED:
      logger.debug(f"Connected: userdata={userdata}; flags={flags}; rc={rc}: {mqtt_client.connack_string(rc)}")
      self.__set_connected_flag(True)
      self.__set_status()

      # Re-subscribe, in case connection was lost
      for topic in self.__list_of_subscribed_topics:
        logger.debug(f"Resubscribe topic: {topic}")
        self.__mqtt.subscribe(topic, self.__qos)

    else:
      logger.error(f"userdata={userdata}; flags={flags}; rc={rc}: {mqtt_client.connack_string(rc)}")
      self.__set_connected_flag(False)

  def __on_disconnect(self, _client, userdata, rc, _properties=None):
    """
    Callback: called when the client disconnects from the broker.

    Args:
      :param ? _client: the client instance for this callback
      :param ? userdata: the private user data as set in Client()
      :param int rc: the disconnection result --> rc_dict
      :param _properties: The MQTT v5.0 properties received from the broker.  A
              list of Properties class instances.

    Returns:
      None
    """
    if rc != mqtt_client.MQTT_ERR_SUCCESS:
      logger.warning(f"Unexpected disconnect, userdata = {userdata}; rc = {rc}: {mqtt_client.error_string(rc)}")
    else:
      logger.info(f"Expected disconnect, userdata = {userdata}; rc = {rc}: {mqtt_client.error_string(rc)}")

    self.__set_connected_flag(False)
    return

  def __on_message(self, _client, _userdata, message):
    """
    :param _client:
    :param _userdata:
    :param message: Queue()
    :return:
    """
    logger.debug(f">> message = {message.topic}  {message.payload}")

    self.__subscribed_queue.put(message)

    # set event that message has been received
    if self.__message_trigger is not None:
      self.__message_trigger.set()

  def __on_publish(self, _client, userdata, mid):
    """
    Callback: when a message that was to be sent using the publish() call has completed transmission to the broker.

    Args:
      :param ? _client: the client instance for this callback
      :param ? userdata: the private user data as set in Client()
      :param ? mid: matches the mid-variable returned from the corresponding publish()

    Returns:
      None
    """
    logger.debug(f"userdata={userdata}; mid={mid}")
    return None

  def __on_subscribe_v5(self, _client, _userdata, mid, reasoncodes, _properties=None):
    """
    :param _client: The client instance for this callback
    :param _userdata: The private user data as set in Client() or userdata_set()
    :param mid: Matches the mid-variable returned from the corresponding subscribe() call.
    :param reasoncodes: The MQTT v5.0 reason codes received from the broker for each
                        subscription.  A list of ReasonCodes instances.
    :param _properties: The MQTT v5.0 properties received from the broker.  A
                      list of Properties class instances.
    :return:
    """
    logger.debug(f"Subscribed mid variable: {mid}")

    for rc in reasoncodes:
      logger.debug(f"reasonCode = {rc}")

  def __on_subscribe_v31(self, _client, _userdata, mid, granted_qos):
    """
    :param _client:
    :param _userdata:
    :param mid:
    :param granted_qos: list of integers that give the QoS level the broker has
                        granted for each of the different subscription requests.
    :return:
    """
    logger.debug(f"Subscribed mid variable: {mid}")

    for qos in granted_qos:
      logger.debug(f"Granted QoS = {qos}")

  def __on_unsubscribe(self, _client, _userdata, mid, _properties=None, _reasoncode=None):
    """
    :param _client:
    :param _userdata:
    :param mid:
    :param _reasoncode:
    :param _properties: The MQTT v5.0 properties received from the broker.  A
           list of Properties class instances.
    :return:
    """
    logger.debug(f">> Unsubscribed: {mid}")

  def __on_log(self, client, _userdata, level, buf):
    """
    Callback: when the client has log information.

    Args:
      :param ? client:
      :param ? _userdata:
      :param ? level: severity of the message
      :param ? buf: message

    Returns:
      None
    """
    logger.debug(f"obj={client}; level={level}; buf={buf}")

  def __set_status(self):
    """
    Publish MQTT status message
    :return: None
    """
    logger.debug(">>")

    if self.__status_topic is not None:
      self.do_publish(self.__status_topic, self.__status_payload, self.__status_retain)

    return

  def set_status(self, topic, payload=None, retain=False):
    """
    Set status
    Will store status & resend on a reconnect

    :param str topic:
    :param str payload:
    :param bool retain:
    :return: None
    """
    logger.debug(">>")
    self.__status_topic = topic
    self.__status_payload = payload
    self.__status_retain = retain
    self.__set_status()

  def will_set(self, topic, payload=None, qos=1, retain=False):
    """
    Set last will/testament
    It is advised to call before self.run() is called

    :param str topic:
    :param str payload:
    :param int qos:
    :param bool retain:
    :return: None
    """
    logger.debug(f">>")

    if self.__run:
      logger.warning(f"Last Will/testament is set after run() is called. Not advised per documentation")

    self.__mqtt.will_set(topic, payload, qos, retain)

  def do_publish(self, topic, message, retain=False):
    """
    Publish topic & message to MQTT broker

    Args:publish(topic, payload=None, qos=0, retain=False)
      :param str topic: MQTT topic
      :param str message: MQTT message
      :param bool retain: retained flag MQTT message

    Returns:
      None
    """
    logger.debug(f">> TOPIC={topic}; MESSAGE={message}")

    try:
      mqttmessageinfo = self.__mqtt.publish(topic=topic, payload=message, qos=self.__qos, retain=retain)
      self.__mqtt_counter += 1

      if mqttmessageinfo.rc != mqtt_client.MQTT_ERR_SUCCESS:
        logger.warning(f"MQTT publish was not successfull, rc = {mqttmessageinfo.rc}: "
                       f"{mqtt_client.error_string(mqttmessageinfo.rc)}")
    except ValueError:
      logger.warning("")

  def set_message_trigger(self, subscribed_queue, trigger=None):
    """
    Call before subscribing
    The received messages are stored in a queue
    If a message is received, trigger event will be set

    :param subscribed_queue: Queue() - as received by on_message (topic, payload,..)
    :param trigger: threading.Event(); OPTIONAL: to indicate that message has been received
    :return:
    """

    self.__message_trigger = trigger
    self.__subscribed_queue = subscribed_queue

    # Re-subscribe, in case connection was lost
    for topic in self.__list_of_subscribed_topics:
      logger.debug(f"Resubscribe topic: {topic}")
      self.__mqtt.subscribe(topic, self.__qos)

    return

  def subscribe(self, topic):
    logger.debug(f">> topic = {topic}")

    # Add to subscribed topic to queue (for resubscribing when reconnecting)
    self.__list_of_subscribed_topics.append(topic)

    if self.__subscribed_queue is None:
      logger.error(f"Subscription message queue has not been set --> call set_message_trigger")
      return

    # Subscribing will not work if client is not connected
    # Wait till there is a connection
    # Todo....not required....just store in list, will be subscribe in on_connect()
    # while not self.__connected_flag and not self.__mqtt_stopper.is_set():
    #  logger.warning(f"No connection with MQTT Broker; cannot subscribe...wait for connection")
    #  time.sleep(0.1)

    self.__mqtt.subscribe(topic, self.__qos)
    return

  def unsubscribe(self, topic):
    """
    Unsubscribe topic
    Use exactly same topic as with subscribe, otherwise topic will not be removed
    from buffer used to restore subscriptions during a reconnect

    :param topic:
    :return:
    """
    logger.debug(f">> topic = {topic}")
    self.__mqtt.unsubscribe(topic)

    try:
      self.__list_of_subscribed_topics.remove(topic)
    except ValueError:
      logger.warning(f"MQTT client was not subscribed to topic '{topic}'; "
                     f"did you use exact same topic as when subscribing?")
    return

  def run(self):
    logger.info(f"Broker = {self.__mqtt_broker}>>")
    self.__run = True

    # Wait till there is network connectivity to mqtt broker
    # Start with a small delay and incrementally (+20%) make larger
    delay = 0.1
    while not self.__internet_on():
      time.sleep(delay)
      delay = delay * 1.2

      # Timeout after 60min
      if delay > 3600:
        logger.error(f"No internet connection - EXIT")
        self.__mqtt_stopper.set()
        self.__worker_threads_stopper.set()
        return

    try:
      # Options functions to be called before connecting
      # Set queue to unlimitted (=65535) when qos>0
      self.__mqtt.max_queued_messages_set(0)
      self.__mqtt.reconnect_delay_set(min_delay=1, max_delay=360)

      # clean_session is only implemented for MQTT v3
      if self.__mqtt_protocol == mqtt_client.MQTTv311 or self.__mqtt_protocol == mqtt_client.MQTTv31:
        self.__mqtt.connect_async(host=self.__mqtt_broker,
                                  port=self.__mqtt_port,
                                  keepalive=self.__keepalive)
      elif self.__mqtt_protocol == mqtt_client.MQTTv5:
        if self.__mqtt_cleansession:
          # TODO
          # For clean_start set to True or Start_first_Only, a session expiry interval
          # has to be set via properties object
          # This is not yet implemented
          self.__mqtt.connect_async(host=self.__mqtt_broker,
                                    port=self.__mqtt_port,
                                    keepalive=self.__keepalive,
                                    clean_start=mqtt_client.MQTT_CLEAN_START_FIRST_ONLY,
                                    properties=None)
        else:
          self.__mqtt.connect_async(host=self.__mqtt_broker,
                                    port=self.__mqtt_port,
                                    keepalive=self.__keepalive,
                                    clean_start=False,
                                    properties=None)
      else:
        logger.error(f"Unknown MQTT protocol version {self.__mqtt_protocol}....exit")
        self.__worker_threads_stopper.set()
        self.__mqtt_stopper.set()

    except Exception as e:
      logger.exception(f"Exception {format(e)}")
      self.__mqtt.disconnect()
      self.__mqtt_stopper.set()
      self.__worker_threads_stopper.set()
      return

    else:
      logger.info(f"Start mqtt loop...")
      self.__mqtt.loop_start()

    # Start infinite loop which sends queued messages every second
    while not self.__mqtt_stopper.is_set():
      # Todo: reconnect stuff needed?

      # Check connection status
      # If disconnected time exceeds threshold
      # then reconnect
      if not self.__connected_flag:
        disconnect_time = int(time.time()) - self.__disconnect_start_time
        logger.debug(f"Disconnect TIMER = {disconnect_time}")
        if disconnect_time > self.__MQTT_CONNECTION_TIMEOUT:
          try:
            self.__mqtt.reconnect()
          except Exception as e:
            logger.exception(f"Exception {format(e)}")

            # reconnect failed....reset disconnect time, and retry after self.__MQTT_CONNECTION_TIMEOUT
            self.__disconnect_start_time = int(time.time())

      time.sleep(0.1)

    # Close mqtt broker
    logger.debug(f"Close down MQTT client & connection to broker")
    self.__mqtt.loop_stop()
    self.__mqtt.disconnect()
    self.__mqtt_stopper.set()
    self.__worker_threads_stopper.set()

    logger.info(f"Shutting down MQTT Client... {self.__mqtt_counter} MQTT messages have been published")

    logger.info(f"<<")
