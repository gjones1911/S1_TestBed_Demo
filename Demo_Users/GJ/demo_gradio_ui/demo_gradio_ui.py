import gradio as gr
import subprocess
import threading
import queue
import time

# Global dictionary to track processes and output queues
processes = {}
output_queues = {}

def read_process_output(proc, q):
    """ Reads the stdout of a running process and stores it in a queue."""
    for line in iter(proc.stdout.readline, b""):
        q.put(line)
    proc.stdout.close()

def start_program(program_name, script_path):
    """Starts the specified script and captures its stdout."""
    if program_name in processes and processes[program_name].poll() is None:
        return f"{program_name} is already running."
   
    q = queue.Queue()
    proc = subprocess.Popen(["python", script_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    processes[program_name] = proc
    output_queues[program_name] = q
    threading.Thread(target=read_process_output, args=(proc, q), daemon=True).start()
    return f"Started {program_name}."

def stop_program(program_name):
    """Stops the specified script if running."""
    if program_name in processes and processes[program_name].poll() is None:
        processes[program_name].terminate()
        processes[program_name].wait()
        return f"Stopped {program_name}."
    return f"{program_name} is not running."

def get_output(program_name):
    """Retrieves the latest output from the script's stdout."""
    if program_name in output_queues:
        output = []
        while not output_queues[program_name].empty():
            output.append(output_queues[program_name].get())
        return "".join(output)
    return "No output available."

# Define UI for each program
def create_ui(program_name, script_path):
    with gr.Blocks() as ui:
        gr.Markdown(f"### {program_name} Controller")
       
        start_btn = gr.Button("Start")
        stop_btn = gr.Button("Stop")
        output_box = gr.Textbox(label="Program Output", lines=10, interactive=False)
       
        start_btn.click(start_program, inputs=[gr.Text(value=program_name, visible=False), gr.Text(value=script_path, visible=False)], outputs=[output_box])
        stop_btn.click(stop_program, inputs=[gr.Text(value=program_name, visible=False)], outputs=[output_box])
       
        def update_output():
            while True:
                output_box.value = get_output(program_name)
                time.sleep(1)
       
        threading.Thread(target=update_output, daemon=True).start()
   
    return ui

# Create UIs for each script
data_streamer_script = r"C:\GitHub\S1_TestBed_Demo\code\S1_Data_MQTT\S1Data_MQTT_Pub.py"
ui_1 = create_ui("Data Streamer", data_streamer_script)
ui_2 = create_ui("Integer Processor", data_streamer_script)
ui_3 = create_ui("String Sender", data_streamer_script)

# Launch the Gradio app with all three UIs
grn = gr.TabbedInterface([ui_1, ui_2, ui_3], ["Data Streamer", "Integer Processor", "String Sender"])
grn.launch()