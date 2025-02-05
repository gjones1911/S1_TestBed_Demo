
## based on https://medium.com/python-point/mqtt-basics-with-python-examples-7c758e605d4
## 

# if the first time: `conda install -c conda-forge paho-mqtt`
# or `pip install paho-mqtt`
import paho.mqtt.client as mqtt
from random import randrange
import time
import uuid

# mqttBroker = "mqtt.eclipseprojects.io"
# mqttBroker = "broker.hivemq.com"
mqttBroker = "recoil.ise.utk.edu"
# mqttBroker ="localhost" 


client_id = f'Publisher_xl_{uuid.uuid4().hex[:8]}'
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id, clean_session=False)

## with pwd
# client.username_pw_set(username="admin",password="secret!99")
client.username_pw_set(username="hivemquser",password="mqAccess2024REC")

client.connect(mqttBroker)

while True:
    randNumber = randrange(10) 
    client.publish("Channel 2 Derived Pk", randNumber)
    randNumber = randrange(0, 1000) / 100
    print(f"Just published {randNumber} to Topic Channel 2 Derived Pk")
    time.sleep(1)