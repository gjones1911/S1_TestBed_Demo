import numpy as np
from transformers import pipeline
from LLM_TOOLS.LLM_Bots import *
import paho.mqtt.client as mqtt
import time
import os
import random


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
topic = 'prediction'

# topic we need to publish to so the DT can see the instructions
to_publish = 'instructions'


# should be path to folder, if it is in this dir you can just use this
Model_Name = r"S1_MotorMaintenaceInstructor"


# get instance of instructor bot while passing either the path to the 
# relevant folder, or the path to a model on hugging face which should consist of either the base name, or a username/model_name
# for instance for me this would be gjonesQ02/S1_InsturctionGeneratorGamma
instructor_Bot = InstructorBot(bot_path=Model_Name, name='Instructor')




##### Utility functions
# callback upon connection
def on_connect(client, userdata, flags, rcode):
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
        service_str = topic
        client.subscribe(service_str) 
        print(f"Subscribed to: {service_str}")
        return



# callback upon message
def on_message(client, userdata, message):
    """
        Method used to process the message recieved on the broker
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
            response, prompt = instructor_Bot.respond_to_task_query(status, rng=False, selection=1, ret_prompt=True)
            
            if "\n\n" in response:
                print("double found")
                responseL = response.split("\n\n")
                response = responseL[0] + responseL[1]
            if "\n\n\n" in response:
                print("triple found")
                responseL = response.split("\n\n\n")
                response = responseL[0] + response[1]
            print("Response:\n", response)
            userdata["response"] = response
            time.sleep(PUBLISH_DELAY)
        else:
            print("No new status received....")
            print("Response:\n", response)
            time.sleep(PUBLISH_DELAY)
        print(f"Publishing to {to_publish}")
        client.publish(to_publish, response.encode('utf-8'), qos=2)
    except Exception as ex:
        print(f"ex: {ex}")





# set up and start the client
def run_mqtt_s1_instructor(client_name=CLIENT_ID, demo_time_out=DEMO_TIME_OUT, try_limit=10):
    """
        The method will attempt to connect to the MQTT broker with a client that is subscribed to the 
        'predicton' topic. If successful it will begin using the S1-Instructor model to send instructions
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
    while trys < try_limit:
        try:
            CLIENT_MOD = str(random.randint(1, 10))
            CLIENT_NAME = CLIENT_ID + f"_{CLIENT_MOD}"
            print(f"\nRunning with client name: {CLIENT_NAME}...\n")
            client = mqtt.Client(client_id=CLIENT_NAME)                                   # sample client, unique name
            client.username_pw_set(username=MQTT_USER,password=MQTT_PWD)
            client.user_data_set({"name": CLIENT_NAME, "previous":"", "response":''})     # sample user data, used to determine when a new prediction is needed
            client.on_message=on_message 
            client.on_connect = on_connect
            client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
            connected = True
            trys = try_limit+1
        except Exception as ex:
            print(f"Issue creating MQTT client:\n{ex}")
            trys += 1
            print(f"Attempting for a {trys+1} try of {try_limit} potential trys.")
            connected = False
    if connected:
        client.loop_start()
        time.sleep(DEMO_TIME_OUT)       # only run for alloted time in seconds secs (as a demo; remove for PROD
        client.loop_stop()
    else:
        if trys >= try_limit:
            print("The try limit was reached...")
            print("Please check the code and or arguments and try again...")

    