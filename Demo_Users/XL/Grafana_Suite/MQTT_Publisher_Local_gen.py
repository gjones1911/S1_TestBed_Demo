
## based on https://medium.com/python-point/mqtt-basics-with-python-examples-7c758e605d4
## 

# if the first time: `conda install -c conda-forge paho-mqtt`
# or `pip install paho-mqtt`
import paho.mqtt.client as mqtt
from random import randrange
import time
import uuid
import json

MQTT_BROKER = "localhost" # local mosquitto broker
# MQTT_USER = "admin"
# MQTT_PWD = "secret!99"
MQTT_USER = "hivemquser"
MQTT_PWD = "mqAccess2024REC"
MQTT_PORT = 1883
# MQTT_TOPIC = "sensors/temperature"

try:
    client_id = f'Pub_xl_{uuid.uuid4().hex[:8]}'
    # client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id, clean_session=False)
    client = mqtt.Client(client_id=client_id, clean_session=False)

    ## with pwd
    client.username_pw_set(username=MQTT_USER,password=MQTT_PWD)

    client.connect(MQTT_BROKER)

    while True:       
        randNumber = randrange(0, 1000) / 10
        # Create a JSON message
        # Include timestamp in ISO 8601 format
        payload = json.dumps({
            "temperature": randNumber,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")  # ISO 8601 UTC format
        })

        # Publish as a JSON object
        client.publish("sensors/temperature", payload)

        print(f"Just published {randNumber} to Topic sensors/temperature")
        time.sleep(1)
except Exception as e:
    print(f"An error occurred: {e}")

