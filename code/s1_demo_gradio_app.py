import gradio as gr
import subprocess
import threading
import time
import signal
import sys
import os
PID_FILE = "/tmp/s1_demo_starter.pid"
# Global variable to track the shell script process
script_process = None

# def tail_log_file(log_file, n=10):
#     """Reads the last N lines of a log file."""
#     try:
#         with open(log_file, 'r', encoding='utf-8') as f:
#             return ''.join(f.readlines()[-n:])
#     except Exception as e:
#         return f"Error reading log file: {e}"

def tail_log_file(log_file, n=10):
    """Reads the last N lines of a log file."""
    try:
        if not os.path.exists(log_file):
            return f"Log file {log_file} does not exist yet."
        with open(log_file, 'r', encoding='utf-8') as f:
            return ''.join(f.readlines()[-n:])
    except Exception as e:
        return f"Error reading log file: {e}"


# def start_script(script_path):
#     """Starts the shell script if it's not already running."""
#     global script_process
#     print(f"script: {script_path}")
#     print("script process", script_process)
#     if script_process and script_process.poll() is None:
#         return "Script is already running."
#     try:
#         cmd = f"source {script_path}"
#         print("cmd: ",cmd)
#         # script_process = subprocess.Popen(["bash", script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         script_process = subprocess.Popen(
#             ["bash", "-i", "-c", cmd], 
#             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         print("script process", script_process)
#         return "Script started successfully."
#     except Exception as e:
#         return f"Error starting script: {e}"

# def stop_script():
#     """Stops the shell script if running."""
#     global script_process
#     print("script process", script_process)
#     if script_process and script_process.poll() is None:
#         script_process.terminate()
#         script_process.wait()
#         return "Script stopped successfully."
#     return "Script is not running."

def start_script(script_path):
    """Starts the shell script if it's not already running."""
    global script_process
    print(f"Starting script: {script_path}")

    if os.path.exists(PID_FILE):
        with open(PID_FILE, "r") as f:
            existing_pid = f.read().strip()
            if existing_pid and os.system(f"ps -p {existing_pid} > /dev/null") == 0:
                return "Script is already running."

    try:
        # Properly execute the script in a way that it runs in the background
        script_process = subprocess.Popen(
            ["bash", "-c", f"exec {script_path} > /dev/null 2>&1 &"],
            # stdout=subprocess.PIPE,
            # stderr=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True  # Ensures the process runs independently
            # shell=False  # Avoid unnecessary shell use
        )
        
        time.sleep(2)  # Allow time for process to initialize
        if os.path.exists(PID_FILE):
            with open(PID_FILE, "r") as f:
                return f"Script started with PID {f.read().strip()}"
        return "Script started, but PID file not found."
        # return "Script started successfully."
    except Exception as e:
        return f"Error starting script: {e}"

def stop_script():
    """Stops the shell script if running."""
    # global script_process
    print("Attempting to stop script...")
    if os.path.exists(PID_FILE):
        with open(PID_FILE, "r") as f:
            pid = f.read().strip()
            if pid and os.system(f"ps -p {pid} > /dev/null") == 0:
                os.system(f"kill -TERM {pid}")
                os.remove(PID_FILE)
                return f"Script (PID {pid}) stopped successfully."
    return "Script is not running."
    # if script_process and script_process.poll() is None:
    #     # script_process.terminate()
    #     # script_process.wait()
    #     # print("Script successfully stopped.")
    #     # return "Script stopped successfully."
    #     os.killpg(os.getpgid(script_process.pid), signal.SIGTERM)
    #     script_process.wait()
    #     print("Script successfully stopped.")
    #     return "Script stopped successfully."
    
    # return "Script is not running."


def fetch_output(log_file, num_lines):
    """Fetches the latest N lines from the log file."""
    return tail_log_file(log_file, n=int(num_lines))

def cleanup_and_exit(signum, frame, app):
    """Ensure the script is stopped before exiting."""
    print("Shutting down...")
    stop_script()
    app.close()
    os._exit(0)  # Force exit without lingering processes






# Define UI for controlling the shell script and viewing logs
def create_ui(program_name, log_file, script_path):
    with gr.Blocks() as ui:
        print(f"script: {script_path}")
        gr.Markdown(f"### {program_name} Controller")

        # functional objects
        start_btn = gr.Button("Start Script")
        stop_btn = gr.Button("Stop Script")
        output_box = gr.Textbox(label="Program Output", lines=10, interactive=False)
        output_btn = gr.Button("Refresh Output")
        num_lines = gr.Number(value=10, label="Number of lines", interactive=True)
        
        # event handling
        
        start_btn.click(start_script, inputs=[gr.Text(value=script_path, visible=False)], outputs=[output_box])
        stop_btn.click(stop_script, outputs=[output_box])
        output_btn.click(fetch_output, inputs=[gr.Text(value=log_file, visible=False), num_lines], outputs=[output_box])
        
    return ui



# from gradio_utils.gradio_utils import *

DataPublisherLOG="./logs/s1_data_mqtt_pub.log"
PredictionPublisherLOG="./logs/s1_prediction_starter.log"
InstructionPublisherLOG="./logs/s1_instructor_starter.log"
# FlagFile="./tmp/s1_instructor_loaded.flag"

# Define paths to log files and script
log_files = {
    "Data Streamer": DataPublisherLOG,
    "Fault Predictor": PredictionPublisherLOG,
    "Maintenance Instructor": InstructionPublisherLOG,
}
script_path = "s1_demo_starter.sh"  # script that start all three program components of the demo (data streamer, predictor, instructor)

# Create UIs for each log file and script control
ui_1 = create_ui("Data Streamer", log_files["Data Streamer"], script_path)
ui_2 = create_ui("Fault Predictor", log_files["Fault Predictor"], script_path)
ui_3 = create_ui("Maintenance Instructor", log_files["Maintenance Instructor"], script_path)

# Launch the Gradio app with shareable link and proper cleanup
share=True
server_port=7895
grn = gr.TabbedInterface([ui_1, ui_2, ui_3], ["Data Streamer", "Fault Predictor", "Maintenance Instructor"])


# Register signal handlers for graceful shutdown
try:
    signal.signal(signal.SIGTERM, lambda sig, frame: cleanup_and_exit(sig, frame, grn))
except Exception as ex:
    print(ex)

try:
    signal.signal(signal.SIGINT, lambda sig, frame: cleanup_and_exit(sig, frame, grn))
except Exception as ex:
    print(ex)
    
try:
    signal.signal(signal.SIGTSTP, lambda sig, frame: cleanup_and_exit(sig, frame, grn))
except Exception as ex:
    print(ex)

# grn.launch(share=share, server_port=server_port)


def run_app(app, share, port=7895, ):
    try:
        app.launch(share=share, server_port=port)
    finally:
        cleanup_and_exit(None, None, app)

run_app(grn, share=True, port=7895)