#!/bin/bash
set -m  # Enable job control
# Check if a duration argument is provided
# Set a default duration value
DEFAULT_DURATION=180

# Use the provided argument or the default value
DURATION=${1:-$DEFAULT_DURATION}
echo "Duration: $DURATION" 

LOGFILE="./logs/startup_debug.log"
exec > >(tee -a $LOGFILE) 2>&1
echo "the log file $LOGFILE"
echo "Script started at $(date)"
echo "Running as PID $$"
PIDFILE="./tmp/s1_demo_starter.pid"

# Ensure the tmp directory exists
mkdir -p ./tmp

echo $$ > $PIDFILE
echo "PID file written successfully at ./tmp/s1_demo_starter.pid"
echo "PID file written successfully at $PIDFILE"

DataPublisherLOG="./logs/s1_data_mqtt_pub.log"
PredictionPublisherLOG="./logs/s1_prediction_starter.log"
InstructionPublisherLOG="./logs/s1_instructor_starter.log"
FlagFile="./tmp/s1_instructor_loaded.flag"

if [ -f $DataPublisherLOG ]; then
   echo "File $DataPublisherLOG exists."
   rm $DataPublisherLOG
else
   echo "File $DataPublisherLOG does not exist."
fi

if [ -f $PredictionPublisherLOG ]; then
   echo "File $PredictionPublisherLOG exists."
   rm $PredictionPublisherLOG
else
   echo "File $PredictionPublisherLOG does not exist."
fi

if [ -f $InstructionPublisherLOG ]; then
   echo "File $InstructionPublisherLOG exists."
   rm $InstructionPublisherLOG
else
   echo "File $InstructionPublisherLOG does not exist."
fi

if [ -f $FlagFile ]; then
   echo "File $FlagFile exists.";
   rm $FlagFile;
else
   echo "File $FlagFile does not exist.";
fi

# Fix: Trap SIGINT to properly kill background processes
trap 'echo "Stopping script..."; for pid in "${PIDS[@]}"; do kill -TERM $pid 2>/dev/null; done; exit 0' SIGINT

# Fix: Wait for background processes properly
PIDS=()   # create list of created process IDs
python -u "./s1_mqtt_instructor/s1_instructor_starter.py"  --duration "$DURATION" > "./logs/s1_instructor_starter.log" 2>&1 &
INSTRUCTOR_PID=$!
PIDS+=($INSTRUCTOR_PID)
echo "instructor pid $INSTRUCTOR_PID"
while [ ! -f "./tmp/s1_instructor_loaded.flag" ]; 
do
    echo "waiting on flag file"
    sleep 2
done

echo "model loaded"

python -u "./RandomForestPredictionMQTT/S1Predict.py" --duration "$DURATION"  > "./logs/s1_prediction_starter.log" 2>&1  &
PREDICTOR_PID=$!
PIDS+=($PREDICTOR_PID)
sleep 2
echo "predictor started"
python -u "./S1_Data_MQTT/S1Data_MQTT_Pub.py" --duration "$DURATION" > "./logs/s1_data_mqtt_pub.log" 2>&1 &
STREAMER_PID=$!
PIDS+=($STREAMER_PID)
echo "data publisher started"

# Cleanup logs at the end
wait "${PIDS[@]}"
echo "All background processes have finished."
rm -f "$DataPublisherLOG" "$PredictionPublisherLOG" "$InstructionPublisherLOG" "$FlagFile" "$PIDFILE"
echo "All scripts have finished running for duration: $DURATION seconds."