#!/bin/bash

# Check if a duration argument is provided
# Set a default duration value
DEFAULT_DURATION=60

# Use the provided argument or the default value
DURATION=${1:-$DEFAULT_DURATION}
echo "Duration: $DURATION" 
set -m  # Enable job control
source ../venvs/s1demovenv/Scripts/activate   # activate the environment

python "C:\Users\iLab\GIT_REPOS\SAFE\S1_TestBed_Demo\S1_TestBed_Demo\code\s1_mqtt_instructor\s1_instructor_starter.py"  --duration "$DURATION" > ./logs/s1_instructor2_starter.log 2>&1 &               # start apps in sequence
python "C:\Users\iLab\GIT_REPOS\SAFE\S1_TestBed_Demo\S1_TestBed_Demo\code\RandomForestPredictionMQTT\S1Predict.py" --duration "$DURATION"  > ./logs/s1_prediction_starter.log 2>&1  &
python "C:\Users\iLab\GIT_REPOS\SAFE\S1_TestBed_Demo\S1_TestBed_Demo\code\S1_Data_MQTT\S1Data_MQTT_Pub.py" --duration "$DURATION" > ./logs/s1_data_mqtt_pub.log 2>&1 &

wait

# Deactivate the virtual environment (optional)
deactivate

echo "All scripts have finished running for duration: $DURATION seconds."