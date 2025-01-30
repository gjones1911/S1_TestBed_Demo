import numpy as np
from transformers import pipeline
from LLM_TOOLS.LLM_Bots import *
import paho.mqtt.client as mqtt
import time
import os
import random

import json
from huggingface_hub import HfApi, login

import argparse


def parse_args():
    # Create an argument parser
    parser = argparse.ArgumentParser(description="Script to run with a specified duration.")
    
    # Add the --duration argument
    parser.add_argument(
        '--duration',
        type=int,
        required=True,
        help="Duration in seconds for the script to run."
    )
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Access the --duration argument
    duration = args.duration
    
    print(f"Running script for {duration} seconds...")
    return duration

## MQTT connection settings
MQTT_PORT = 1883
MQTT_KEEPALIVE = 60
DEMO_TIME_OUT = 7200                    # how long before the demo will run before stopping (uses sleep)
PUBLISH_DELAY=5
CLIENT_ID = "S1_Fault_Instructor"
MQTT_BROKER = "recoil.ise.utk.edu"

MQTT_USER = "hivemquser"
MQTT_PWD = "mqAccess2024REC"


## keep track of when a new status appears to cut down on 
## how often we have to get a new query from the bot
status = ""
old_status = ""
response = ""
topic = 'motor_state'

# prediction we need to get to send which instruction set to generate
subscription_topic = 'prediction'

# topic we need to publish to so the DT can see the instructions
publish_topic = 'instructions'

# should be path to folder, if it is in this dir you can just use this
Model_Name = r"S1_MotorMaintenaceInstructor"


# get instance of instructor bot while passing either the path to the 
# relevant folder, or the path to a model on hugging face which should consist of either the base name, or a username/model_name
# for instance for me this would be gjonesQ02/S1_InsturctionGeneratorGamma
instructor_Bot = InstructorBot(bot_path=Model_Name, name='Instructor')

# will login and if the ""add_git_cred" is set to True, will store them for future operations
def set_up_hf_login(HF_Token_json, add_git_cred=True):
    # use file to get tokens
    with open(HF_Token_json, 'r') as jfile:
        tokens = json.load(jfile)
    
    read_token = tokens.get("Get")
    write_token = tokens.get("Push")
    
    api_hf = HfApi()
    
    if read_token:
        # api_hf.set_access_token(read_token)
        login(token=read_token, add_to_git_credential=add_git_cred)
        print("successful read token setup")
    else:
        print("Some issue with read token for HF")
    
    if write_token:
        # api_hf.set_access_token(write_token)
        login(token=read_token, add_to_git_credential=add_git_cred)
        print("successful write token setup")
    else:
        print("Some issue with write token for HF")



class InstructorMqttClient:
    def __init__(self, instruction_assistant=instructor_Bot, 
                client_name="Instruction_Assistant_", 
                subscription_topic=subscription_topic, publish_topic=publish_topic, 
                *kwargs):
        self.subscription_topic=subscription_topic
        self.publish_topic = publish_topic
        self.client_name = client_name
        self.instruction_assistant=instruction_assistant


    ##### Utility functions
    # callback upon connection
    def on_connect(self, client, userdata, flags, rcode):
        """
            Method used to connect to and subscribe to the needed topics on the MQTT connection
        """
        print("Connected flags ",str(flags),"result code ",str(rcode))
        if (rcode != 0): # handle error
            print("MQTT auth failed")
            os._exit(1) # works - hard exit
        else:
            # if connection was successful subscribe to the "prediction" channel
            print("Connection successful!")
            service_str = self.subscription_topic
            client.subscribe(service_str) 
            print(f"\n\n\tSubscribed to: {service_str}")
            print(f"\n\n\tPublishing to: {self.publish_topic}\n\n\n")
            return



    # callback upon message
    def on_message(self, client, userdata, message):
        """
            Method used to process the message received on the broker
            and determine which instruction set to send. The method 
            will only query the LLM if a new fault is seen. 
            
        """
        print(f"Message received: {message.payload.decode('utf-8')}")
        try:
            status = int(message.payload.decode("utf-8"))
            status_decoder = {
                0: "baseline",
                1: "bent_shaft",
                2: "eccentric_rotor",
                3: "offset_misalignment",
                4: "resonance_beam",
                5: "imbalance",
                6: "faulted_coupling",
                7: "faulted_bearing",
                8: "angular_misalignment",
                9: "looseness",
            }

            # pull string version of status from int version mapping
            status = status_decoder[status]
            response = userdata["response"]
            
            # check for new motor state
            # if so actual get a generation
            # otherwise use the old one
            if status != userdata['previous']:
                # old_status = status
                userdata['previous'] = status
                print("new status received: ", status)
                print("Please wait for the response...")
                response, prompt = self.instruction_assistant.respond_to_task_query(status, rng=False, selection=1, ret_prompt=True)
                
                # Logic used to strip excess new lines from instructions
                if "\n\n" in response:
                    responseL = response.split("\n\n")
                    response = responseL[0] + responseL[1]
                if "\n\n\n" in response:
                    responseL = response.split("\n\n\n")
                    response = responseL[0] + response[1]
                print("Response:\n", response)
                userdata["response"] = response
                time.sleep(PUBLISH_DELAY)
            else:
                print("No new status received....")
                print("Response:\n", response)
                time.sleep(PUBLISH_DELAY)
            print(f"Publishing to {self.publish_topic}")
            client.publish(self.publish_topic, response.encode('utf-8'), qos=2)
        except Exception as ex:
            print(f"ex: {ex}")


    def create_client(self, client_name=CLIENT_ID, username=MQTT_USER, pwd=MQTT_PWD,
                    mqtt_broker=MQTT_BROKER, mqtt_port=MQTT_PORT, mqtt_keepalive=MQTT_KEEPALIVE,
                    ):
        client = mqtt.Client(client_id=client_name)                                   # sample client, unique name
        client.username_pw_set(username=username,password=pwd)
        client.user_data_set({"name": client_name, "previous":"", "response":''})     # sample user data, used to determine when a new prediction is needed
        client.on_message=self.on_message 
        client.on_connect = self.on_connect
        client.connect(mqtt_broker, mqtt_port, mqtt_keepalive)
        return client

    # set up and start the client
    def run_mqtt_s1_instructor(self, client_name=CLIENT_ID, demo_time_out=DEMO_TIME_OUT, try_limit=10):
        """
            The method will attempt to connect to the MQTT broker with a client that is subscribed to the 
            'prediction' topic. If successful it will begin using the S1-Instructor model to send instructions
            over the MQTT connection on the topic 'instruction' for some number of seconds based on the 
            demo_time_out argument. It will make 'try_limit' attempts before if stops and sends a message 
            on std-out to alert the user. 
            Arguments:
                client_name (str): name of client_id for MQTT client. Needs to be unique, default='S1_Fault_Instructor'"
                demo_time_out (int): the number of seconds the demo will run before it times out and stops
                try_limit (int): the number of trys that will be made to make the connection, after which the program will quit
            Returns:
                None
        """
        connected = False
        trys = 0
        print(f"Set to run for {demo_time_out} seconds...")
        while trys < try_limit:
            try:
                CLIENT_MOD = str(random.randint(1, 10))
                CLIENT_NAME = client_name + f"_{CLIENT_MOD}"
                print(f"\n\nRunning with client name: {CLIENT_NAME}...\n\n")
                # client = mqtt.Client(client_id=CLIENT_NAME)                                   # sample client, unique name
                # client.username_pw_set(username=MQTT_USER,password=MQTT_PWD)
                # client.user_data_set({"name": CLIENT_NAME, "previous":"", "response":''})     # sample user data, used to determine when a new prediction is needed
                # client.on_message=self.on_message 
                # client.on_connect = self.on_connect
                client = self.create_client(client_name=CLIENT_NAME, )
                # client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
                connected = True
                trys = try_limit+1
            except Exception as ex:
                print(f"Issue creating MQTT client:\n{ex}")
                trys += 1
                print(f"Attempting for a {trys+1} try of {try_limit} potential trys.")
                connected = False
        if connected:
            client.loop_start()
            time.sleep(demo_time_out)       # only run for alloted time in seconds secs (as a demo; remove for PROD
            client.loop_stop()
        else:
            if trys >= try_limit:
                print("The try limit was reached...")
                print("Please check the code and or arguments and try again...")


class PredictorMqttClient(InstructorMqttClient):
    def __init__(self, prediction_assistant=None, 
                client_name="Fault_State_Assistant_", 
                subscription_topic=subscription_topic, publish_topic=publish_topic, 
                **kwargs):
        super().__init__(
            # prediction_assistant=prediction_assistant,
            client_name=client_name, 
            subscription_topic=subscription_topic, 
            publish_topic=publish_topic, 
            **kwargs,
        )
        self.prediction_assistant=prediction_assistant
        
        
    ##### Utility functions
    # callback upon connection
    def on_connect(self, client, userdata, flags, rcode):
        """
            Method used to connect to and subscribe to the needed topics on the MQTT connection
        """
        print("Connected flags ",str(flags),"result code ",str(rcode))
        if (rcode != 0): # handle error
            print("MQTT auth failed")
            os._exit(1) # works - hard exit
        else:
            # if connection was successful subscribe to the "prediction" channel
            print("Connection successful!")
            service_str = self.subscription_topic
            client.subscribe(service_str) 
            print(f"\n\n\tSubscribed to: {service_str}")
            print(f"\n\n\tPublishing to: {self.publish_topic}\n\n\n")
            return

    def run_predictions_loop(self, interval_sec=10, topic="prediction", 
                            try_limit=10, duration=60,
                            ):
        
        connected = False
        trys = 0
        
        while trys < try_limit:
            try:
                CLIENT_MOD = str(random.randint(1, 10))
                CLIENT_NAME = self.client_name + f"_{CLIENT_MOD}"
                print(f"\n\nRunning with client name: {CLIENT_NAME}...\n\n")
                client = self.create_client(client_name=CLIENT_NAME, )
                connected = True
                trys = try_limit+1
            except Exception as ex:
                print(f"Issue creating MQTT client:\n{ex}")
                trys += 1
                print(f"Attempting for a {trys+1} try of {try_limit} potential trys.")
                connected = False
        if connected:
            time_left = True
            ts = time.time()
            while time_left:
                # send a prediction and wait...
                prediction = 2
                prediction = 3
                print(f"Sending Prediction: {prediction}")
                client.publish(topic, prediction, qos=2)
                time.sleep(interval_sec)
                time_spent = time.time() - ts
                time_left = time_spent < duration
        else:
            print("Issue with connection!!!!!!!")