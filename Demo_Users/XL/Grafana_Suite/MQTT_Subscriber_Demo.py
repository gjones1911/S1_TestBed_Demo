import paho.mqtt.client as mqtt
import time
import uuid

# Configuration
# MQTT_BROKER = "recoil.ise.utk.edu"
# MQTT_USER = "hivemquser"
# MQTT_PWD = "mqAccess2024REC"
# MQTT_PORT = 1883
MQTT_TOPIC = "json_data"

MQTT_BROKER = "localhost"
MQTT_USER = "hivemquser"
MQTT_PWD = "mqAccess2024REC"
# MQTT_USER = "admin"
# MQTT_PWD = "secret!99"
MQTT_PORT = 1883
# MQTT_TOPIC = "sensors/temperature"

RUN_DURATION = 600  # in seconds

def on_message(client, userdata, message):
    print(f"Received message -> {message.topic}:{message.payload.decode()}")

def main():
    client_id = f'Sub_xl_{uuid.uuid4().hex[:8]}'
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id, clean_session=False)
    
    client.username_pw_set(username=MQTT_USER, password=MQTT_PWD)
    client.on_message = on_message

    try:
        client.connect(MQTT_BROKER, MQTT_PORT)
        print(f"Connected to {MQTT_BROKER}")

        client.subscribe(MQTT_TOPIC)
        client.loop_start()

        time.sleep(RUN_DURATION)

        client.loop_stop()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
