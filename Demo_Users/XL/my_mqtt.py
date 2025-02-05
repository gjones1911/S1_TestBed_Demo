import paho.mqtt.client as mqtt
import json
import time
import uuid
import logging
from logging.handlers import RotatingFileHandler
import os
import threading

# Create log directory if it doesn't exist
log_dir = 'log'
os.makedirs(log_dir, exist_ok=True)

# Configure logging
log_file_path = os.path.join(log_dir, 'my_mqtt.log')
logging.basicConfig(level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(log_file_path, maxBytes=5*1024*1024, backupCount=5),
        logging.StreamHandler()
    ])

# MQTT broker details
MQTT_BROKER = "recoil.ise.utk.edu"
MQTT_USER = "hivemquser"
MQTT_PWD = "mqAccess2024REC"
MQTT_PORT = 1883

class MyMQTT:
    def __init__(self, broker=MQTT_BROKER, port=MQTT_PORT, user=MQTT_USER, password=MQTT_PWD):
        self.broker = broker
        self.port = port
        self.user = user
        self.password = password
        self.client_id = f'mqtt_{uuid.uuid4().hex[:12]}'
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=self.client_id, clean_session=False)
        self.broker_connection_status = False
        self.latest_payload = None
        self.stop_event = threading.Event()

        # Assign the callback functions
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

        # Set the username and password for the MQTT broker
        self.client.username_pw_set(username=self.user, password=self.password)

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            self.broker_connection_status = True
            logging.info(f"Connected to MQTT Broker with Client ID: {self.client_id}")
        else:
            logging.error(f"Failed to connect, return code {rc}")

    def on_disconnect(self, client, userdata, rc, *args, **kwargs):
        self.broker_connection_status = False
        logging.warning(f"Disconnected from MQTT Broker with return code {rc}")

    def on_message(self, client, userdata, message):
        try:
            payload = message.payload.decode("utf-8")
            self.latest_payload = json.loads(payload) if message.topic == "json_data" else {f"{message.topic}": payload}
            self.latest_payload['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

            # Create data directory if it doesn't exist
            data_dir = 'data'
            os.makedirs(data_dir, exist_ok=True)

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

    def get_latest_payload(self):
        return self.latest_payload
    
    def subscribe(self, topic):
        def run_subscription():
            try:
                self.client.subscribe(topic)
                logging.info(f"Subscribed to topic: {topic}")
                while not self.stop_event.is_set():
                    self.client.loop()
                    time.sleep(1)
            except Exception as e:
                logging.error(f"An error occurred: {e}")

        subscription_thread = threading.Thread(target=run_subscription)
        subscription_thread.daemon = True
        subscription_thread.start()

    def disconnect(self):
        self.stop_event.set()
        self.client.disconnect()
        self.client.loop_stop()
        logging.info("Disconnected from MQTT Broker")

# Example usage
if __name__ == "__main__":
    mqtt_client = MyMQTT()
    mqtt_client.connect()
    mqtt_client.subscribe("Channel 1 Direct RMS")  # sample json_data

    try:
        while True:
            time.sleep(1)
            payload = mqtt_client.get_latest_payload()
            if payload:
                print(f"Latest payload: {payload}")
            else:
                print("No new payload received.")
    except KeyboardInterrupt:
        mqtt_client.disconnect()
        logging.info("Program terminated by user")
