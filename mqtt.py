#!/usr/bin/env python

import paho.mqtt.client as paho  # pip install paho-mqtt
import broadlink  # pip install broadlink
import os
import sys
import time
import logging
import logging.config
import socket

# read initial config files
logging.config.fileConfig('logging.conf')
CONFIG = os.getenv('BROADLINKMQTTCONFIG', 'mqtt.conf')


class Config(object):
    def __init__(self, filename=CONFIG):
        self.config = {}
        execfile(filename, self.config)

    def get(self, key, default=None):
        return self.config.get(key, default)


try:
    cf = Config()
except Exception, e:
    print "Cannot load configuration from file %s: %s" % (CONFIG, str(e))
    sys.exit(2)

qos = cf.get('mqtt_qos', 0)
retain = cf.get('mqtt_retain', False)

topic_prefix = cf.get('mqtt_topic_prefix', 'broadlink/')


# noinspection PyUnusedLocal
def on_message(mosq, device, msg):
    logging.debug("Received MQTT message " + msg.topic + " " + str(msg.payload))
    command = msg.topic[len(topic_prefix):]
    file = "commands/" + command

    try:
        if os.path.isfile(file):
            with open(file, 'rb') as f:
                ir_packet = f.read()
            device.send_data(ir_packet.decode('hex'))
        else:
            logging.debug("Recording command to file " + file)
            # receive packet
            device.enter_learning()
            ir_packet = None
            attempt = 0
            while ir_packet is None and attempt < 6:
                time.sleep(5)
                ir_packet = device.check_data()
                attempt = attempt + 1
            if ir_packet is not None:
                # write to file
                directory = os.path.dirname(file)
                if not os.path.exists(directory):
                    os.makedirs(directory)
                with open(file, 'wb') as f:
                    f.write(str(ir_packet).encode('hex'))
                logging.debug("Done")
            else:
                logging.warn("No command received")
    except Exception:
        logging.exception("I/O error")


# noinspection PyUnusedLocal
def on_connect(mosq, device, result_code):
    topic = topic_prefix + '#'
    logging.debug("Connected to MQTT broker, subscribing to topic " + topic)
    mqttc.subscribe(topic, qos)


# noinspection PyUnusedLocal
def on_disconnect(mosq, device, rc):
    logging.debug("OOOOPS! Broadlink disconnects")
    time.sleep(10)


if __name__ == '__main__':
    local_address = cf.get('local_address', None)
    timeout = 20
    devices = broadlink.discover(timeout=timeout) if local_address is None else \
        broadlink.discover(timeout=timeout, local_ip_address=local_address)
    if len(devices) == 0:
        logging.error('No Broadlink device found')
        sys.exit(2)
    if len(devices) > 1:
        logging.error('More than one Broadlink device found (' + ', '.join([d.host for d in devices]) + ')')
        sys.exit(2)
        
    device = devices[0]
    device.auth()
    logging.debug('Connected to %s Broadlink device at %s' % (device.type, device.host))

    clientid = cf.get('mqtt_clientid', 'broadlink-%s' % os.getpid())
    # initialise MQTT broker connection
    mqttc = paho.Client(clientid, clean_session=cf.get('mqtt_clean_session', False), userdata=device)

    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_disconnect = on_disconnect

    mqttc.will_set('clients/broadlink', payload="Adios!", qos=0, retain=False)

    # Delays will be: 3, 6, 12, 24, 30, 30, ...
    # mqttc.reconnect_delay_set(delay=3, delay_max=30, exponential_backoff=True)

    mqttc.username_pw_set(cf.get('mqtt_username'), cf.get('mqtt_password'))
    mqttc.connect(cf.get('mqtt_broker', 'localhost'), int(cf.get('mqtt_port', '1883')), 60)

    while True:
        try:
            mqttc.loop_forever()
        except socket.error:
            time.sleep(5)
        except KeyboardInterrupt:
            sys.exit(0)
