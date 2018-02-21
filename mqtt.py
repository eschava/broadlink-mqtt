#!/usr/bin/env python

import paho.mqtt.client as paho  # pip install paho-mqtt
import broadlink  # pip install broadlink
import os
import sys
import time
import logging
import logging.config
import socket
import sched
HAVE_TLS = True
try:
    import ssl
except ImportError:
    HAVE_TLS = False
from threading import Thread
from test import TestDevice

# read initial config files
dirname = os.path.dirname(os.path.abspath(__file__)) + '/'
logging.config.fileConfig(dirname + 'logging.conf')
CONFIG = os.getenv('BROADLINKMQTTCONFIG', dirname + 'mqtt.conf')


class Config(object):
    def __init__(self, filename=CONFIG):
        self.config = {}
        self.config['ca_certs']     = None
        self.config['tls_version']  = None
        self.config['certfile']     = None
        self.config['keyfile']      = None
        self.config['tls_insecure'] = False
        self.config['tls']          = False
        execfile(filename, self.config)

        if HAVE_TLS == False:
            logging.error("TLS parameters set but no TLS available (SSL)")
            sys.exit(2)

        if self.config.get('ca_certs') is not None:
            self.config['tls'] = True

        if self.config.get('tls_version') is not None:
            if self.config.get('tls_version') == 'tlsv1':
                self.config['tls_version'] = ssl.PROTOCOL_TLSv1
            if self.config.get('tls_version') == 'tlsv1.2':
                # TLS v1.2 is available starting from python 2.7.9 and requires openssl version 1.0.1+.
                if sys.version_info >= (2,7,9):
                    self.config['tls_version'] = ssl.PROTOCOL_TLSv1_2
                else:
                    logging.error("TLS version 1.2 not available but 'tlsv1.2' is set.")
            	    sys.exit(2)
            if self.config.get('tls_version') == 'sslv3':
                self.config['tls_version'] = ssl.PROTOCOL_SSLv3

    def get(self, key, default='special empty value'):
        v = self.config.get(key, default)
        if v == 'special empty value':
            logging.error("Configuration parameter '%s' should be specified" % key)
            sys.exit(2)
        return v


try:
    cf = Config()
except Exception, e:
    print "Cannot load configuration from file %s: %s" % (CONFIG, str(e))
    sys.exit(2)

qos = cf.get('mqtt_qos', 0)
retain = cf.get('mqtt_retain', False)

topic_prefix = cf.get('mqtt_topic_prefix', 'broadlink/')


# noinspection PyUnusedLocal
def on_message(client, device, msg):
    command = msg.topic[len(topic_prefix):]

    if command == 'temperature' or command == 'energy' or command.startswith('sensor/'):  # internal notification
        return

    try:
        action = str(msg.payload)
        logging.debug("Received MQTT message " + msg.topic + " " + action)

        if command == 'power':
            if device.type == 'SP1' or device.type == 'SP2':
                state = action == 'on'
                logging.debug("Setting power state to {0}".format(state))
                device.set_power(1 if state else 0)
                return

            if device.type == 'MP1':
                parts = action.split("/", 2)
                if len(parts) == 2:
                    sid = int(parts[0])
                    state = parts[1] == 'on'
                    logging.debug("Setting power state of socket {0} to {1}".format(sid, state))
                    device.set_power(sid, state)
                    return

        if device.type == 'RM2':
            file = dirname + "commands/" + command

            if action == '' or action == 'auto':
                record_or_replay(device, file)
                return
            elif action == 'record':
                record(device, file)
                return
            elif action == 'replay':
                replay(device, file)
                return
            elif action == 'macro':
                file = dirname + "macros/" + command
                macro(device, file)
                return

        logging.debug("Unrecognized MQTT message " + action)
    except Exception:
        logging.exception("Error")


# noinspection PyUnusedLocal
def on_connect(client, device, flags, result_code):
    topic = topic_prefix + '#'
    logging.debug("Connected to MQTT broker, subscribing to topic " + topic)
    mqttc.subscribe(topic, qos)


# noinspection PyUnusedLocal
def on_disconnect(client, device, rc):
    logging.debug("OOOOPS! Broadlink disconnects")
    time.sleep(10)


def record_or_replay(device, file):
    if os.path.isfile(file):
        replay(device, file)
    else:
        record(device, file)


def record(device, file):
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


def replay(device, file):
    logging.debug("Replaying command from file " + file)
    with open(file, 'rb') as f:
        ir_packet = f.read()
    device.send_data(ir_packet.decode('hex'))


def macro(device, file):
    logging.debug("Replaying macro from file " + file)
    with open(file, 'rb') as f:
        for line in f:
            line = line.strip(' \n\r\t')
            if len(line) == 0 or line.startswith("#"):
                continue
            if line.startswith("pause "):
                pause = int(line[6:].strip())
                logging.debug("Pause for " + str(pause) + " milliseconds")
                time.sleep(pause / 1000.0)
            else:
                command_file = dirname + "commands/" + line
                replay(device, command_file)


def get_device(cf):
    device_type = cf.get('device_type', 'lookup')
    if device_type == 'lookup':
        local_address = cf.get('local_address', None)
        lookup_timeout = cf.get('lookup_timeout', 20)
        devices = broadlink.discover(timeout=lookup_timeout) if local_address is None else \
            broadlink.discover(timeout=lookup_timeout, local_ip_address=local_address)
        if len(devices) == 0:
            logging.error('No Broadlink device found')
            sys.exit(2)
        if len(devices) > 1:
            logging.error('More than one Broadlink device found (' + ', '.join([d.host for d in devices]) + ')')
            sys.exit(2)
        return devices[0]
    elif device_type == 'test':
        return TestDevice(cf)
    else:
        host = (cf.get('device_host'), 80)
        mac = bytearray.fromhex(cf.get('device_mac').replace(':', ' '))
        if device_type == 'rm':
            return broadlink.rm(host=host, mac=mac)
        elif device_type == 'sp1':
            return broadlink.sp1(host=host, mac=mac)
        elif device_type == 'sp2':
            return broadlink.sp2(host=host, mac=mac)
        elif device_type == 'a1':
            return broadlink.a1(host=host, mac=mac)
        elif device_type == 'mp1':
            return broadlink.mp1(host=host, mac=mac)
        else:
            logging.error('Incorrect device configured: ' + device_type)
            sys.exit(2)


def broadlink_rm_temperature_timer(scheduler, delay, device):
    scheduler.enter(delay, 1, broadlink_rm_temperature_timer, [scheduler, delay, device])

    try:
        temperature = str(device.check_temperature())
        topic = topic_prefix + "temperature"
        logging.debug("Sending RM temperature " + temperature + " to topic " + topic)
        mqttc.publish(topic, temperature, qos=qos, retain=retain)
    except:
        logging.exception("Error")


def broadlink_sp_energy_timer(scheduler, delay, device):
    scheduler.enter(delay, 1, broadlink_sp_energy_timer, [scheduler, delay, device])

    try:
        energy = str(device.get_energy())
        topic = topic_prefix + "energy"
        logging.debug("Sending SP energy " + energy + " to topic " + topic)
        mqttc.publish(topic, energy, qos=qos, retain=retain)
    except:
        logging.exception("Error")


def broadlink_a1_sensors_timer(scheduler, delay, device):
    scheduler.enter(delay, 1, broadlink_a1_sensors_timer, [scheduler, delay, device])

    try:
        sensors = device.check_sensors_raw()
        for name in sensors:
            topic = topic_prefix + "sensor/" + name
            value = str(sensors[name])
            logging.debug("Sending A1 " + name + " " + value + " to topic " + topic)
            mqttc.publish(topic, value, qos=qos, retain=retain)
    except:
        logging.exception("Error")


class SchedulerThread(Thread):
    def __init__(self, scheduler):
        Thread.__init__(self)
        self.scheduler = scheduler

    def run(self):
        try:
            self.scheduler.run()
        except:
            logging.exception("Error")


if __name__ == '__main__':
    device = get_device(cf)
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

    if cf.get('tls') == True:
        mqttc.tls_set(cf.get('ca_certs'), cf.get('certfile'), cf.get('keyfile'), tls_version=cf.get('tls_version'), ciphers=None)

    if cf.get('tls_insecure'):
        mqttc.tls_insecure_set(True)

    mqttc.username_pw_set(cf.get('mqtt_username'), cf.get('mqtt_password'))
    mqttc.connect(cf.get('mqtt_broker', 'localhost'), int(cf.get('mqtt_port', '1883')), 60)

    broadlink_rm_temperature_interval = cf.get('broadlink_rm_temperature_interval', 0)
    if device.type == 'RM2' and broadlink_rm_temperature_interval > 0:
        scheduler = sched.scheduler(time.time, time.sleep)
        scheduler.enter(broadlink_rm_temperature_interval, 1, broadlink_rm_temperature_timer,
                        [scheduler, broadlink_rm_temperature_interval, device])
        # scheduler.run()
        tt = SchedulerThread(scheduler)
        tt.daemon = True
        tt.start()

    broadlink_sp_energy_interval = cf.get('broadlink_sp_energy_interval', 0)
    if device.type == 'SP2' and broadlink_sp_energy_interval > 0:
        scheduler = sched.scheduler(time.time, time.sleep)
        scheduler.enter(broadlink_sp_energy_interval, 1, broadlink_sp_energy_timer,
                        [scheduler, broadlink_sp_energy_interval, device])
        # scheduler.run()
        tt = SchedulerThread(scheduler)
        tt.daemon = True
        tt.start()

    broadlink_a1_sensors_interval = cf.get('broadlink_a1_sensors_interval', 0)
    if device.type == 'A1' and broadlink_a1_sensors_interval > 0:
        scheduler = sched.scheduler(time.time, time.sleep)
        scheduler.enter(broadlink_a1_sensors_interval, 1, broadlink_a1_sensors_timer,
                        [scheduler, broadlink_a1_sensors_interval, device])
        # scheduler.run()
        tt = SchedulerThread(scheduler)
        tt.daemon = True
        tt.start()

    while True:
        try:
            mqttc.loop_forever()
        except socket.error:
            time.sleep(5)
        except KeyboardInterrupt:
            sys.exit(0)
        except:
            logging.exception("Error")

