import paho.mqtt.client as mqtt
import time

import os
import sys
import numpy as np
import pandas as pd

import joblib

# MQTT Broker
MQTT_BROKER = 'recoil.ise.utk.edu'
# MQTT Username/Pwd
MQTT_USER = 'hivemquser'
MQTT_PWD = 'mqAccess2024REC'


def generate_motor_topics(motor_number):
    channels = ['ch1', 'ch2']
    metrics = ['bias', 'derivedPk', 'directRMS', 'direct', 'velocityRMS', 'velocityPk']
    
    topics = [f'Motor{motor_number}/{ch}_{metric}' for ch in channels for metric in metrics]
    return topics

# Generate topics for Motor1, Motor2, and Motor3
# MotorMock is a 'mock' motor
Motor1_topics = generate_motor_topics(1)
Motor2_topics = generate_motor_topics(2)
Motor3_topics = generate_motor_topics(3)


print(Motor1_topics)
print(Motor2_topics)
print(Motor3_topics)

# Topics to suscribe to
S1_topics = ['Channel 1 Bias',
             'Channel 1 DerivedPk',
             'Channel 1 DirectRMS',
             'Channel 1 Direct',
             'Channel 1 VelocityPk',
             'Channel 1 VelocityRMS',
             'Channel 2 Bias',
             'Channel 2 DerivedPk',
             'Channel 2 DirectRMS',
             'Channel 2 Direct',
             'Channel 2 VelocityPk',
             'Channel 2 VelocityRMS']


curdir = os.getcwd()
print(curdir)

# Loading random forest model
# replace with path to model trained & pickled locally (S1 Server)
with open (f'{curdir}/RandomForestPredictionMQTT/model/rf_joblib.z', 'rb') as f:
    rf = joblib.load(f)

# Creating empty dictionary to store messages

messages = {
    'Motor1': {topic: None for topic in Motor1_topics},
    'Motor2': {topic: None for topic in Motor2_topics},
    'Motor3': {topic: None for topic in Motor3_topics},
    'S1': {topic: None for topic in S1_topics}
}

# Global variable for start time
start_time  = time.time()

def model_predict(messages, motor):
    df = pd.DataFrame([messages])
    prediction = rf.predict(df)
    if prediction[0] == 9:
        prediction = '2'
    print(f'Prediction for {motor}: ', prediction[0])
    client.publish(f'{motor}/prediction', str(prediction[0]), qos = 2)
    client.publish('prediction', str(prediction[0]), qos = 2)
    

def on_message(client, userdata, message):
    global start_time

    topic = message.topic
    payload = message.payload.decode('utf-8')
    if topic in S1_topics:
        motor = 'S1'
    else:
        motor = topic.split('/')[0]
    messages[motor][topic] = payload
    print('Received message: ', message.topic, str(payload))
    
    # setting the predictions to every 10 seconds, after the start of receiving a message.
    global start_time
    if time.time() - start_time >= 10:
        for motor in messages:
            model_predict(messages[motor], motor)
        start_time = time.time()

mqttBroker = MQTT_BROKER

client = mqtt.Client(client_id='S1RandomForestClient')

## with pwd

client.username_pw_set(username = MQTT_USER, password = MQTT_PWD)
client.connect(mqttBroker)

#client.loop_start()

for motor_topics in [Motor1_topics, Motor2_topics, Motor3_topics, S1_topics]:
    for topic in motor_topics:
        client.subscribe(topic)

client.loop_start()
start_time = time.time()
client.on_message = on_message


print(messages)

# How long the whole program runs
time.sleep(10000)

client.loop_stop()

