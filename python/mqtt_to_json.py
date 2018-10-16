import paho.mqtt.client as mqtt
import json
import requests
import logging
import pathlib
from configparser import ConfigParser


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)

# Read config file
config = ConfigParser()
config.read('iot.cfg')
region = config.get('TTN', 'Region')
appid = config.get('TTN', 'AppID')
appkey = config.get('TTN', 'AppKey')

json_filename = "/data/data.json"


def on_connect(mqttc, obj, flags, rc):
    logger.info("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    mqttc.subscribe("+/devices/+/up", qos=0)


def on_disconnect(mqttc, obj, rc):
    if rc != 0:
        logger.warning("Unexpected disconnection.")


def on_message(mqttc, obj, msg):
    logger.info("Received message '" + str(msg.payload) + "' on topic '" + msg.topic + "' with QoS " + str(msg.qos))
    if msg.retain==1:
        logger.info("This is a retained message.")
    #msg_json = json.loads(str(msg.payload.decode("utf-8")))
    json_str = str(msg.payload.decode("utf-8"))

    # Write the full JSON received from the TTN MQTT topic to a file.
    with open(json_filename, "a") as json_file:
        json_file.write(f'\n{json_str}')


def on_publish(mqttc, obj, mid):
    logger.info("Messaged ID: " + str(mid))


def on_subscribe(mqttc, obj, mid, granted_qos):
    logger.info("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(mqttc, obj, level, string):
    logger.log(level, string)


mqttc = mqtt.Client()

mqttc.enable_logger(logger)

mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
# Uncomment to enable debug messages
# mqttc.on_log = on_log

mqttc.username_pw_set(appid, appkey)
mqttc.connect("{}.thethings.network".format(region), 1883, 60)

mqttc.loop_forever()
