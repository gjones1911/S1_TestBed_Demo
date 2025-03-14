# Set script duration
$DURATION = 180
Write-Output "Duration: $DURATION"

# Define log file paths
$LOGFILE = "./logs/startup_debug.log"
$DataPublisherLOG = "./logs/s1_data_mqtt_pub.log"
$DataPublisherERR = "./logs/s1_data_mqtt_pub.err"
$PredictionPublisherLOG = "./logs/s1_prediction_starter.log"
$PredictionPublisherERR = "./logs/s1_prediction_starter.err"
$InstructionPublisherLOG = "./logs/s1_instructor_starter.log"
$InstructionPublisherERR = "./logs/s1_instructor_starter.err"
$FlagFile = "./tmp/s1_instructor_loaded.flag"

# Ensure the ./tmp/ directory exists
New-Item -ItemType Directory -Path "./tmp" -Force | Out-Null

# Start logging output
Start-Transcript -Path $LOGFILE -Append

# Remove existing logs and flag file before starting
Remove-Item -Path $DataPublisherLOG, $DataPublisherERR, $PredictionPublisherLOG, $PredictionPublisherERR, $InstructionPublisherLOG, $InstructionPublisherERR, $FlagFile -ErrorAction Ignore

# Store PIDs of running processes
$PIDS = @()

# Function to stop processes and clean up logs
function Cleanup {
    Write-Output "Stopping script..."
    
    # Stop all running Python processes
    foreach ($pid in $PIDS) {
        if (Get-Process -Id $pid -ErrorAction SilentlyContinue) {
            Stop-Process -Id $pid -Force -ErrorAction Ignore
            Write-Output "Killed process $pid"
        }
    }

    # Ensure all processes have stopped before continuing
    Start-Sleep -Seconds 2
    $remaining = Get-Process | Where-Object { $_.ProcessName -like "python*" }
    if ($remaining) {
        Write-Output "Forcing termination of remaining Python processes..."
        Stop-Process -Name "python" -Force -ErrorAction Ignore
    }

    # Stop transcript before deleting logs
    Stop-Transcript
    Start-Sleep -Seconds 5  # Give PowerShell time to release file handles

    Write-Output "Attempting to delete log files..."
    
    # Retry log file deletion to ensure they are released
    $retryCount = 5
    while ($retryCount -gt 0) {
        try {
            Remove-Item -Path $DataPublisherLOG, $DataPublisherERR, $PredictionPublisherLOG, $PredictionPublisherERR, $InstructionPublisherLOG, $InstructionPublisherERR, $FlagFile -Force -ErrorAction Stop
            Write-Output "Log files deleted successfully."
            break
        } catch {
            Write-Output "Log files still in use, retrying ($retryCount attempts left)..."
            Start-Sleep -Seconds 2
            $retryCount--
        }
    }

    Write-Output "Cleanup complete. Exiting."
    exit 0
}

# Start instructor process **WITHOUT opening a new terminal**, but writing output to logs
$instructor = Start-Process -FilePath "python" `
    -ArgumentList "-u ./s1_mqtt_instructor/s1_instructor_starter.py --duration $DURATION" `
    -RedirectStandardOutput $InstructionPublisherLOG `
    -RedirectStandardError $InstructionPublisherERR `
    -NoNewWindow -PassThru
$PIDS += $instructor.Id
Write-Output "Instructor started with PID $($instructor.Id)"

# Wait for the flag file before proceeding
Write-Output "Waiting for flag file: $FlagFile"
while (!(Test-Path $FlagFile)) {
    Write-Output "Still waiting for flag file..."
    Start-Sleep -Seconds 2
}

Write-Output "Instructor model loaded! Proceeding with the rest of the processes."

# Start predictor process **WITHOUT opening a new terminal**, but writing output to logs
$predictor = Start-Process -FilePath "python" `
    -ArgumentList "-u ./RandomForestPredictionMQTT/S1Predict.py --duration $DURATION" `
    -RedirectStandardOutput $PredictionPublisherLOG `
    -RedirectStandardError $PredictionPublisherERR `
    -NoNewWindow -PassThru
$PIDS += $predictor.Id
Write-Output "Predictor started with PID $($predictor.Id)"

# Start data streamer process **WITHOUT opening a new terminal**, but writing output to logs
$streamer = Start-Process -FilePath "python" `
    -ArgumentList "-u ./S1_Data_MQTT/S1Data_MQTT_Pub.py --duration $DURATION" `
    -RedirectStandardOutput $DataPublisherLOG `
    -RedirectStandardError $DataPublisherERR `
    -NoNewWindow -PassThru
$PIDS += $streamer.Id
Write-Output "Data streamer started with PID $($streamer.Id)"

# Ensure cleanup happens when the script exits
try {
    # Monitor for Ctrl+C manually while waiting for processes
    while ($true) {
        Start-Sleep -Seconds 1
        if ($Host.UI.RawUI.KeyAvailable) {
            $key = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
            if ($key.VirtualKeyCode -eq 3) {  # 3 is the code for Ctrl+C
                break
            }
        }
    }
}
finally {
    Cleanup
}
