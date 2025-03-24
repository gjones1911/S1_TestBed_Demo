# import gradio as gr
# import subprocess
# import threading
# import time
# import signal
# import sys
# import os

# def tail_log_file(log_file, n=10):
#     """Reads the last N lines of a log file."""
#     try:
#         with open(log_file, 'r', encoding='utf-8') as f:
#             return ''.join(f.readlines()[-n:])
#     except Exception as e:
#         return f"Error reading log file: {e}"

# # Global variable to track the shell script process
# script_process = None

# def start_script(script_path):
#     """Starts the shell script if it's not already running."""
#     global script_process
#     if script_process and script_process.poll() is None:
#         return "Script is already running."
#     try:
#         script_process = subprocess.Popen(["bash", script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         return "Script started successfully."
#     except Exception as e:
#         return f"Error starting script: {e}"

# def stop_script():
#     """Stops the shell script if running."""
#     global script_process
#     if script_process and script_process.poll() is None:
#         script_process.terminate()
#         script_process.wait()
#         return "Script stopped successfully."
#     return "Script is not running."

# def fetch_output(log_file, num_lines):
#     """Fetches the latest N lines from the log file."""
#     return tail_log_file(log_file, n=int(num_lines))

# def cleanup_and_exit(signum, frame):
#     """Ensure the script is stopped before exiting."""
#     print("Shutting down...")
#     stop_script()
#     os._exit(0)  # Force exit without lingering processes

# # Register signal handlers for graceful shutdown
# signal.signal(signal.SIGINT, cleanup_and_exit)
# signal.signal(signal.SIGTERM, cleanup_and_exit)
# signal.signal(signal.SIGTSTP, cleanup_and_exit)


# # Define UI for controlling the shell script and viewing logs
# def create_ui(program_name, log_file, script_path):
#     with gr.Blocks() as ui:
#         gr.Markdown(f"### {program_name} Controller")

#         # functional objects
#         start_btn = gr.Button("Start Script")
#         stop_btn = gr.Button("Stop Script")
#         output_box = gr.Textbox(label="Program Output", lines=10, interactive=False)
#         output_btn = gr.Button("Refresh Output")
#         num_lines = gr.Number(value=10, label="Number of lines", interactive=True)
        
#         # event handling
#         start_btn.click(start_script, inputs=[gr.Text(value=script_path, visible=False)], outputs=[output_box])
#         stop_btn.click(stop_script, outputs=[output_box])
#         output_btn.click(fetch_output, inputs=[gr.Text(value=log_file, visible=False), num_lines], outputs=[output_box])
        
#     return ui



from gradio_utils.gradio_utils import *

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
grn.launch(share=share, server_port=server_port)