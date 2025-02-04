from my_mqtt import *

# Create an instance of MyMQTT
my_mqtt = MyMQTT()
print(f"paylod = {my_mqtt.latest_payload}")
my_mqtt.subscribe("Channel 1 Direct")

print(f"paylod = {my_mqtt.latest_payload}")
