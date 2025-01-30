#!/bin/bash

# Check if a duration argument is provided
# Set a default duration value
DEFAULT_DURATION=60

# Use the provided argument or the default value
DURATION=${1:-$DEFAULT_DURATION}
echo "Duration: $DURATION" 
set -m  # Enable job control
source ../venvs/s1demovenv/Scripts/activate   # activate the environment

python "C:\Users\iLab\Desktop\GIT_REPOS\SAFE_GITS\S1_TestBed_Demo\code\s1_instructor_starter.py"  --duration "$DURATION" > s1_instructor_starter.log 2>&1 &               # start apps in sequence
python "C:\Users\iLab\Desktop\GIT_REPOS\SAFE_GITS\S1_TestBed_Demo\code\s1_predictions_starter.py" --duration "$DURATION"  > s1_prediction_starter.log 2>&1  &
#python3 script3.py &

wait

# Deactivate the virtual environment (optional)
deactivate

echo "All scripts have finished running for duration: $DURATION seconds."