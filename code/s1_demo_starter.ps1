# PowerShell version of the script
$DURATION = 180
Write-Output "Duration: $DURATION"

$LOGFILE = "./logs/startup_debug.log"
New-Item -ItemType File -Path $LOGFILE -Force | Out-Null
Start-Transcript -Path $LOGFILE -Append

$PIDFILE = "./tmp/s1_demo_starter.pid"
New-Item -ItemType Directory -Path "./tmp" -Force | Out-Null
Write-Output "$PID" | Out-File -FilePath $PIDFILE -Encoding utf8

$DataPublisherLOG = "./logs/s1_data_mqtt_pub.log"
$PredictionPublisherLOG = "./logs/s1_prediction_starter.log"
$InstructionPublisherLOG = "./logs/s1_instructor_starter.log"
$FlagFile = "./tmp/s1_instructor_loaded.flag"

Remove-Item -Path $DataPublisherLOG, $PredictionPublisherLOG, $InstructionPublisherLOG, $FlagFile -ErrorAction Ignore

# Start background processes
$PIDS = @()

$instructor = Start-Process -FilePath "python" -ArgumentList "-u ./s1_mqtt_instructor/s1_instructor_starter.py --duration $DURATION" -PassThru
$PIDS += $instructor.Id

while (!(Test-Path $FlagFile)) {
    Write-Output "waiting on flag file"
    Start-Sleep -Seconds 2
}

Write-Output "model loaded"

$predictor = Start-Process -FilePath "python" -ArgumentList "-u ./RandomForestPredictionMQTT/S1Predict.py --duration $DURATION" -PassThru
$PIDS += $predictor.Id

Start-Sleep -Seconds 2
Write-Output "predictor started"

$streamer = Start-Process -FilePath "python" -ArgumentList "-u ./S1_Data_MQTT/S1Data_MQTT_Pub.py --duration $DURATION" -PassThru
$PIDS += $streamer.Id

Write-Output "data publisher started"

# Properly handle Ctrl+C (SIGINT)
$trapHandler = {
    Write-Output "Stopping script..."
    foreach ($pid in $PIDS) {
        Stop-Process -Id $pid -Force -ErrorAction Ignore
    }
    Remove-Item -Path $PIDFILE, $DataPublisherLOG, $PredictionPublisherLOG, $InstructionPublisherLOG, $FlagFile -ErrorAction Ignore
    Write-Output "All scripts have finished running."
    Stop-Transcript
    exit 0
}
Register-ObjectEvent -InputObject $host -EventName "Exiting" -Action $trapHandler

Wait-Process -Id $PIDS

# Cleanup
Write-Output "All background processes have finished."
Remove-Item -Path $PIDFILE, $DataPublisherLOG, $PredictionPublisherLOG, $InstructionPublisherLOG, $FlagFile -ErrorAction Ignore
Write-Output "All scripts have finished running for duration: $DURATION seconds."

Stop-Transcript
