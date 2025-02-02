import paho.mqtt.client as mqtt
import time

import os
import sys
import numpy as np
import pandas as pd
import json
import joblib
import argparse
import signal
pid = str(os.getpid())
# MQTT Broker
MQTT_BROKER = 'recoil.ise.utk.edu'
# MQTT Username/Pwd
MQTT_USER = 'hivemquser'
MQTT_PWD = 'mqAccess2024REC'

def parse_args():
    # Create an argument parser
    parser = argparse.ArgumentParser(description="Script to run with a specified duration.")
    
    # Add the --duration argument
    parser.add_argument(
        '--duration',
        type=int,
        required=False,
        help="Duration in seconds for the script to run.",
        default=120,
    )
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Access the --duration argument
    duration = args.duration
    
    print(f"data publisher Running script for {duration} seconds...")
    return duration


duration = parse_args()

def generate_motor_topics(motor_number):
    channels = ['ch1', 'ch2']
    metrics = ['bias', 'derivedPk', 'directRMS', 'direct', 'velocityRMS', 'velocityPk']
    
    topics = [f'Motor{motor_number}/{ch}_{metric}' for ch in channels for metric in metrics]
    return topics

# expected order
og = ['ch1_bias', 'ch1_derivedPk', 'ch1_directRMS', 'ch1_direct', 'ch1_velocityRMS', 'ch1_velocityPk', 
    'ch2_bias', 'ch2_derivedPk', 'ch2_directRMS', 'ch2_direct', 'ch2_velocityRMS', 'ch2_velocityPk']
desired_order = [
    'Channel 1 Bias', 'Channel 1 Derived Pk', 'Channel 1 Direct RMS', 'Channel 1 Direct', 
    'Channel 1 Velocity RMS', 'Channel 1 Velocity Pk',
    
    'Channel 2 Bias', 'Channel 2 Derived Pk', 'Channel 2 Direct RMS', 'Channel 2 Direct',  
    'Channel 2 Velocity RMS', 'Channel 2 Velocity Pk',  ]
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
            'Channel 2 VelocityRMS', 
            ]

extra_topic = ["json_data"]

S1_topics += extra_topic
curdir = os.getcwd()
print("current directory:\n", curdir)

# Loading random forest model
# replace with path to model trained & pickled locally (S1 Server)
model_path = f'{curdir}/RandomForestPredictionMQTT/model/rf_joblib.z'
model_path = f'{curdir}/RandomForestModel/rf_model/rf_joblib.pk'
with open (model_path, 'rb') as f:
    rf = joblib.load(f)


# print rf to check that it loaded
# print(f"RF: {rf}")
# Creating empty dictionary to store messages
messages = {
    'Motor1': {topic: None for topic in Motor1_topics},
    'Motor2': {topic: None for topic in Motor2_topics},
    'Motor3': {topic: None for topic in Motor3_topics},
    'S1': {topic: None for topic in S1_topics}
}
print(f"here:{messages}")
# Global variable for start time
start_time  = time.time()

def model_predict(messages, motor):
    try:
        print(f"messages: {messages}")
        df = pd.DataFrame([messages])
        print(f"\n\n\n\t\tOG--->df:\n{df}\n")
        prediction = rf.predict(df)
        if prediction[0] == 9:
            print("\n\n\n\t\tAdjustment aws made!!!!")
            prediction = '2'
        print(f'Prediction for {motor}: ', prediction[0])
        client.publish(f'{motor}/prediction', str(prediction[0]), qos = 2)
        client.publish('prediction', str(prediction[0]), qos = 2)
    except Exception as ex:
        print(f"Error with model predict:\nMotor: {motor}\n:exception: {ex}\n---------------------\n\n")
    

def on_message(client, userdata, message):
    # global start_time

    topic = message.topic
    if topic != extra_topic[0]:
        payload = message.payload.decode('utf-8')
        if topic in S1_topics:
            motor = 'S1'
        else:
            motor = topic.split('/')[0]
            messages[motor][topic] = payload
        print(f"topic: {topic}")
        print('Received message: ', message.topic, str(payload))
    
        # setting the predictions to every 10 seconds, after the start of receiving a message.
        global start_time
        if time.time() - start_time >= 10:
            for motor in messages:
                model_predict(messages[motor], motor)
            start_time = time.time()
        else:
            print(f"next prediction in {(time.time() - start_time)-10:.2f} seconds")
    else:
        try:
            data = json.loads(message.payload.decode('utf-8'))
            print(f'json-data: {data}')
            # pull the data into a dataframe, drop unneeded column and reorder columns as needed
            df = pd.DataFrame(data, index=[0]).drop(columns=['Volts'])[desired_order]
            # print(f"columns: {df.columns}")
            # print(f"df:\n{df}\n")
            
            prediction = str(rf.predict(df)[0])
            if prediction == "9":
                print("Adjusting value to 2")
                prediction = "2"
            print(f"prediction: {prediction}")
            client.publish('prediction', str(prediction[0]), qos = 2)
        except Exception as ex:
            print(f"22ex:{ex}")
            

def on_connect(client, userdata, flags, rc, properties):
    print(f"Connected with result code {rc}")
    
    if rc == 0:
        print("Connected successfully")
        for motor_topics in [Motor1_topics, Motor2_topics, Motor3_topics, S1_topics]:
            for topic in motor_topics:
                print(f"Subscribing to: {topic}")
                client.subscribe(topic)
    else:
        print(f"Connection failed with code {rc}")
        if rc == 4:
            print("Bad username/password. Check credentials.")
        elif rc == 5:
            print("Not authorized. Check broker permissions.")






##########################################################
# client creation
mqttBroker = MQTT_BROKER
print("makeing client")
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f'S1RandomForestClientab_{pid}', clean_session=True)
# client = mqtt.Client(client_id='S1RandomForestClient')
## with pwd
client.username_pw_set(username = MQTT_USER, password = MQTT_PWD)
client.on_message = on_message
client.on_connect = on_connect
MQTT_PORT = 1883
MQTT_KEEPALIVE = 6000
MQTT_KEEPALIVE = 60
client.connect(mqttBroker, MQTT_PORT, MQTT_KEEPALIVE)
# client.connect(mqttBroker)
# Global flag to track running state
running = True

def graceful_exit(signum, frame):
    """Handle script shutdown gracefully."""
    global running
    print("\nGraceful shutdown initiated...")
    
    running = False  # Stop main loop
    
    print("Disconnecting MQTT client...")
    client.disconnect()
    
    print("Stopping MQTT loop...")
    client.loop_stop()
    
    print("Exiting program.")
    sys.exit(0)

# Attach signal handlers
try:
    signal.signal(signal.SIGINT, graceful_exit)   # Ctrl+C
except Exception as ex:
    print(ex)
try:
    signal.signal(signal.SIGTERM, graceful_exit)  # Kill command
except Exception as ex:
    print(ex)
try:
    signal.signal(signal.SIGHUP, graceful_exit)   # Terminal close
except Exception as ex:
    print(ex)
try:
    signal.signal(signal.SIGQUIT, graceful_exit)  # Quit command (Ctrl+\)
except Exception as ex:
    print(ex)
#client.loop_start()

# for motor_topics in [Motor1_topics, Motor2_topics, Motor3_topics, S1_topics]:
#     for topic in motor_topics:
#         print(f"Subscribing to: {topic}")
#         client.subscribe(topic)

client.loop_start()
start_time = time.time()



print(messages)
print("Sleeping until...")
# How long the whole program runs
# time.sleep(duration)

try:
    while running:
        time.sleep(duration)  # Keep main thread alive
except Exception as e:
    print(f"Unexpected error: {e}")
    graceful_exit(None, None)

client.loop_stop()

