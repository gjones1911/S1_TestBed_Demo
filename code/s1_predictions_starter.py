"""
    Purpose: This script will attempt to start sending instructions for the S1 test bed motor over the MQTT connection. 
             See 's1_instruction_utils.py' for how it all or to adjust the MQTT settings
"""
from s1_instruction_utils import *


# login to Huggingface to ensure 
# HF_Token_json = "../data/credentials/HF_Tokens.json"
# set_up_hf_login(HF_Token_json)


# make default instructor object
# this sets up the client in terms
# * broker information
# * name of client
# * topic the client will publish to
# * topic the client will subscribe to
# * the LLM assistant that will serve as the instructor
mqtt_predictor = PredictorMqttClient(
    client_name="Fault_prediction_assistant",
    publish_topic='prediction',
)

# set the number of seconds 
# the instructor will run
DEMO_TIME_OUT=60 # seconds

loop_count = 20
interval_sec = 10
topic='prediction'
try_limit = 10

# start the instruction production messaging process
if __name__ == "__main__":
    duration = parse_args()
    print(f"\n\nDuration: {duration}\n\n")
    mqtt_predictor.run_predictions_loop(loop_count, interval_sec=interval_sec, topic=topic, 
                            try_limit=try_limit, duration=duration
                            )