#!/bin/bash

# Check if a duration argument is provided
# Set a default duration value
DEFAULT_DURATION=180

# Use the provided argument or the default value
DURATION=${1:-$DEFAULT_DURATION}
echo "Duration: $DURATION" 
set -m  # Enable job control
source ../venvs/s1demovenv/Scripts/activate   # activate the environment
pwd;

rm /logs/s1_data_mqtt_pub.log
rm /logs/s1_instructor_starter.log
rm /logs/s1_prediction_starter.log

python "./s1_mqtt_instructor/s1_instructor_starter.py"  --duration "$DURATION" > "./logs/s1_instructor_starter.log" 2>&1 &

while [ [ ! -f "/tmp/s1_instructor_loaded.flag" ] ] 
do
    echo "waiting on flag file"
    sleep 2
done

echo "model loaded"

python "./RandomForestPredictionMQTT/S1Predict.py" --duration "$DURATION"  > "./logs/s1_prediction_starter.log" 2>&1  &
sleep 2
python "./S1_Data_MQTT/S1Data_MQTT_Pub.py" --duration "$DURATION" > "./logs/s1_data_mqtt_pub.log" 2>&1 &

wait


rm /logs/s1_data_mqtt_pub.log
rm /logs/s1_instructor_starter.log
rm /logs/s1_prediction_starter.log

echo "All scripts have finished running for duration: $DURATION seconds."

# Deactivate the virtual environment (optional)
deactivate