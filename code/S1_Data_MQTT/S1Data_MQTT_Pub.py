import pandas as pd
from opcua import Client
import time
import paho.mqtt.client as mqtt
import uuid

import json
import argparse
import numpy as np


def parse_args():
    # Create an argument parser
    parser = argparse.ArgumentParser(description="Script to run with a specified duration.")
    
    # Add the --duration argument
    parser.add_argument(
        '--duration',
        type=int,
        required=False,
        help="Duration in seconds for the script to run.",
        default=10,
    )
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Access the --duration argument
    duration = args.duration
    
    print(f"data publisher Running script for {duration} seconds...")
    return duration


duration = parse_args()


# list of nodes for subscribing
subs = {'Channel 1 Direct': 'ns=4;s=f31b1e1d-0b0a-44a3-8b5e-d3378890054b',
        'Channel 1 Direct RMS':'ns=4;s=58e345ff-c79f-48c3-97c5-1f45bb78bddf',
        'Channel 1 Derived Pk':'ns=4;s=d0e181c9-3b65-4e7b-83fc-075b3d96d0c8', 
        'Channel 1 Velocity Pk':'ns=4;s=44fde9ef-62ff-4d58-8079-115a2021fbb4', 
        'Channel 1 Velocity RMS':'ns=4;s=b1a66e0a-3bb7-4ed6-8a0a-9ce5edd87191', 
        'Channel 1 Bias':'ns=4;s=2524679b-2405-4196-801a-cbd01bc750d1', 
        'Channel 2 Direct':'ns=4;s=8eb809b1-225e-46ab-8624-c17c25cb5a93', 
        'Channel 2 Direct RMS':'ns=4;s=2cf96113-ab23-4024-9d63-ebcd55a84977', 
        'Channel 2 Derived Pk':'ns=4;s=1d5c1f0a-8bf4-4887-8db3-7ffea18c8410', 
        'Channel 2 Velocity Pk':'ns=4;s=285ef46b-7c88-4aeb-92b9-419a26320867',
        'Channel 2 Velocity RMS':'ns=4;s=734875fc-c3fa-4128-92f6-6a8c57618420', 
        'Channel 2 Bias':'ns=4;s=0d63b2dc-2ee8-48a9-8358-d584dda813d7'}

# additional nodes for subscribing (high frequency)
hf_subs = {'Channel 1 Demod Wf(2000Hz)': 'ns=4;s=77ce0dbe-6cd6-465a-aed1-725b114af6fc',
           'Channel 1 Accl Wf(5000Hz)': 'ns=4;s=56a70275-e96b-466c-aecd-f77603087c62',
           'Channel 2 Demod Wf(2000Hz)': 'ns=4;s=cfce6899-8583-41e9-b076-c45605388707',
           'Channel 2 Accl Wf(5000Hz)': 'ns=4;s=46e1aa3f-0604-427c-bd6d-9f327bafb0b5'}

# Inverted key:values for mapping
inverse_subs = {v: k for k, v in subs.items()}
inverse_hf_subs = {v: k for k, v in hf_subs.items()}

# temp store for the data
data = {'Channel 1 Direct':[],
        'Channel 1 Direct RMS':[],
        'Channel 1 Derived Pk':[], 
        'Channel 1 Velocity Pk':[], 
        'Channel 1 Velocity RMS':[], 
        'Channel 1 Bias':[], 
        'Channel 2 Direct':[], 
        'Channel 2 Direct RMS':[], 
        'Channel 2 Derived Pk':[], 
        'Channel 2 Velocity Pk':[],
        'Channel 2 Velocity RMS':[], 
        'Channel 2 Bias':[],
        'Volts': []}

def append_data(node_key, value):
    # if there is no data in the index/key added the first
    # otherwise just overwrite the last
    if node_key in data:
        # data[node_key].append(value)
        if len(data[node_key]) > 0:
            data[node_key][0] = value
        else:
            data[node_key].append(value)
    else:
        print(f'{node_key} not found in dictionary.')

# For OPC UA
class SubHandler(object):
    def datachange_notification(self, node, val, data):
        #print("Python: New data change event", node, val)
        # print(f"\n\nData: {data}")
        node_key = str(inverse_subs[str(node)])
        append_data(node_key, val)
        # print(f'Python: New data change event\n:node_key:{node_key}\nval:{val}\n')

    def event_notification(self, event):
        print("Python: New event", event)
        
# For MQTT Client creation (data publisher)

MQTT_BROKER = "localhost" # local mosquitto broker, 
MQTT_USER = "hivemquser"
MQTT_PWD = "mqAccess2024REC"
MQTT_PORT = 1883
MQTT_TOPIC = "sensors/temperature"

client_id = f'Pub_s1_{uuid.uuid4().hex[:8]}'

pub_client = mqtt.Client(client_id=client_id)
pub_client.username_pw_set(username = MQTT_USER, password = MQTT_PWD)


def publishing_data():
    while True:
        print(f"Data-->: {data}")
        json_package = {}
        for key, values in data.items():
            
            # while values:
            if len(values) == 0:
                value = 0
                json_package[key] = 0
            else:
                json_package[key] = np.around(values[-1], 4)
                # value = values.pop(0) # remove first element
                value = np.around(values[-1], 4) # get last added element
                topic = f'{key}'
                pub_client.publish(f's1/{topic}', value, qos = 0)
                print(f'Gathered Data: s1/{topic}, val: {value:.04f}')
         
        json_package['timestamp']  = time.strftime("%Y-%m-%dT%H:%M:%SZ") 
        
        json_payload = json.dumps(json_package)
        # attempt to publish new json payload
        print("publishing on 'json_data'")
        print(json_payload)
        pub_client.publish("json_data", json_payload,qos=0)
        time.sleep(1)

if __name__ == "__main__":
    # connect with opcua client
    client = Client("opc.tcp://SMARTSHOTS:7560/System1OPCUAServer")  
    try:
        client.connect()
        
        # Create a subscription
        subscription = client.create_subscription(500, SubHandler())  # 500 ms publishing interval
        
        pub_client.connect(MQTT_BROKER, keepalive = 1000)
        
        # Subscribe to a data change events for each node in the subs (set)
        #handle = subscription.subscribe_data_change(client.get_node("ns=4;s=6166f712-292e-403c-8b9f-0a093ffea11b")) 
        for key in subs:
            handle = subscription.subscribe_data_change(client.get_node(subs[key]))
            
        publishing_data()
        
        # Keep the client running to receive notifications
        while True:
            pass

    finally:
        client.disconnect()
        print("\n\nFinal data:\n", data, "\n\n")