"""
    Purpose: This script will attempt to start sending instructions for the S1 test bed motor over the MQTT connection. 
             See 's1_instruction_utils.py' for how it all or to adjust the MQTT settings
"""
from s1_instruction_utils import *



# run_mqtt_s1_instructor(client_name=CLIENT_ID, demo_time_out=DEMO_TIME_OUT, try_limit=10)


if __name__ == "__main__":
    run_mqtt_s1_instructor(client_name=CLIENT_ID, demo_time_out=DEMO_TIME_OUT, try_limit=10)