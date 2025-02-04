import paho.mqtt.client as mqtt
import json
import time
import uuid
import logging
from logging.handlers import RotatingFileHandler
import os

# Create log directory if it doesn't exist
log_dir = 'log'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Configure logging
log_file_path = os.path.join(log_dir, 'my_mqtt.log')
logging.basicConfig(level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(log_file_path, maxBytes=5*1024*1024, backupCount=5),
        logging.StreamHandler()
    ])

# MQTT broker details
MQTT_BROKER = "recoil.ise.utk.edu"  # Broker address
MQTT_USER = "hivemquser"            # Username for MQTT broker
MQTT_PWD = "mqAccess2024REC"        # Password for MQTT broker
MQTT_PORT = 1883                    # Port for MQTT broker

class MyMQTT:
    def __init__(self, broker=MQTT_BROKER, port=MQTT_PORT, user=MQTT_USER, password=MQTT_PWD):
        self.broker = broker
        self.port = port
        self.user = user
        self.password = password
        self.client_id = f'subscriber_{uuid.uuid4().hex}'
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=self.client_id, clean_session=False)
        self.broker_connection_status = False
        self.latest_payload = None

        # Assign the callback functions
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

        # Set the username and password for the MQTT broker
        self.client.username_pw_set(username=self.user, password=self.password)

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            self.broker_connection_status = True
            logging.info("Connected to MQTT Broker!")
        else:
            logging.error(f"Failed to connect, return code {rc}")

    def on_disconnect(self, client, userdata, rc, *args, **kwargs):
        self.broker_connection_status = False
        logging.warning(f"Disconnected from MQTT Broker with return code {rc}")

    def on_message(self, client, userdata, message):
        try:
            payload = message.payload.decode("utf-8")
            if message.topic == "json_data": # sample topic
                self.latest_payload = json.loads(payload)
            else:
                self.latest_payload = {f"{message.topic}": payload}
            self.latest_payload['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

            # Create data directory if it doesn't exist
            data_dir = 'data'
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)

            # Append the payload to the data file
            data_file_path = os.path.join(data_dir, 'data.json')
            if not os.path.exists(data_file_path):
                with open(data_file_path, "w") as f:
                    f.write("[]")

            with open(data_file_path, "r+") as f:
                data = json.load(f)
                data.append(self.latest_payload)
                f.seek(0)
                json.dump(data, f, indent=4)
            logging.info(f"Received message: {self.latest_payload}")
        except json.JSONDecodeError as e:
            logging.error(f"Failed to decode JSON payload: {e}")

    def connect(self):
        while not self.broker_connection_status:
            try:
                self.client.connect(self.broker, self.port)
                self.client.loop_start()
                while not self.broker_connection_status:
                    time.sleep(1)
            except Exception as e:
                logging.error(f"Connection failed: {e}. Retrying in 5 seconds...")
                time.sleep(5)

    def subscribe(self, topic):
        try:
            self.client.subscribe(topic)
            logging.info(f"Subscribed to topic: {topic}")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Interrupted by user, stopping...")
            self.disconnect()
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            self.disconnect()

    def disconnect(self):
        self.client.disconnect()
        self.client.loop_stop()
        logging.info("Disconnected from MQTT Broker")

# Example usage
if __name__ == "__main__":
    mqtt_client = MyMQTT()
    mqtt_client.connect()
    # mqtt_client.subscribe("#") # all topics
    ## Note one subscribe at a time, as it is a single thread
    mqtt_client.subscribe("json_data") # json_data
    # mqtt_client.subscribe("Channel 2 Bias") # sample topic: Channel 2 Bias