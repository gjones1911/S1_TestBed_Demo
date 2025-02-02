"""
    Purpose: This script will attempt to start sending instructions for the S1 test bed motor over the MQTT connection. 
             See 's1_instruction_utils.py' for how it all or to adjust the MQTT settings
"""
from s1_instruction_utils import *
print(curdir)

# a file is used as a flag to indicate when the model has completed loading
# to help ensure everything sinks up. To make this work we need to remove the flag
# first thing we do
flag_file = curdir + "/tmp" + "/s1_instructor_loaded.flag"
uncheck_flag_file(flag_file)


# expected order of data points
og = ['ch1_bias', 'ch1_derivedPk', 'ch1_directRMS', 'ch1_direct', 'ch1_velocityRMS', 'ch1_velocityPk', 
    'ch2_bias', 'ch2_derivedPk', 'ch2_directRMS', 'ch2_direct', 'ch2_velocityRMS', 'ch2_velocityPk']
print(curdir)
print(Model_Name)
print(f"inside instruction_starter: {default_model_path}")

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
tstart = time.time()
mqtt_instructor = InstructorMqttClient(
    instruction_assistant_path=default_model_path,
)
tend = time.time() - tstart

print(f"Instructor model loading complete at {tend:.2f} seconds. setting flag")
check_flag_file(flag_file)
print(f"Flag file {flag_file} has been created...")



# start the instruction production messaging process
if __name__ == "__main__":
    # set the number of seconds 
    # the instructor will run based
    # on the default or command line 
    # indicated duration
    duration = parse_args()
    print(f"\n\nDuration: {duration}\n\n")
    mqtt_instructor.run_mqtt_s1_instructor(client_name=CLIENT_ID, demo_time_out=duration, try_limit=10)