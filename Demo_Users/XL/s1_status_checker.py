import paho.mqtt.client as mqtt
import json

# MQTT broker details
MQTT_BROKER = "recoil.ise.utk.edu"  # Broker address
MQTT_USER = "hivemquser"            # Username for MQTT broker
MQTT_PWD = "mqAccess2024REC"        # Password for MQTT broker
MQTT_PORT = 1883                    # Port for MQTT broker

# Global variables
connection_status = False
latest_payload = None

# Callback function when the client connects to the broker
def on_connect(client, userdata, flags, rc, properties=None):
    global connection_status
    connection_status = True
    print(f"Connected with result code {rc}")
    # Access unused parameters to avoid warnings
    _ = client, userdata, flags, properties


# Callback function when a message is received from the broker
def on_message(client, userdata, message):
    global latest_payload
    payload = message.payload.decode("utf-8")
    latest_payload = json.loads(payload)
    print(latest_payload)
    
    # Access unused parameters to avoid warnings
    _ = client, userdata

# Main code
try:
    # Create an MQTT client instance
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id='subscriber_xl_101', clean_session=False)

    # Assign the callback functions
    client.on_connect = on_connect
    client.on_message = on_message

    # Set the username and password for the MQTT broker
    client.username_pw_set(username=MQTT_USER, password=MQTT_PWD)

    # Connect to the MQTT broker
    client.connect(MQTT_BROKER, MQTT_PORT)

    # Subscribe to the desired topic
    client.subscribe("json_data")  # Subscribe to json only

    # Start the MQTT client loop
    client.loop_forever()
except KeyboardInterrupt:
    print("Interrupted by user, stopping...")
    client.disconnect()
    client.loop_stop()
