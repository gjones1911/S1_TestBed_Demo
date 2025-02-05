import gradio as gr
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates  # For datetime formatting on the x-axis
import time
import threading
import datetime
import json

from my_mqtt import MyMQTT

mqtt_client = MyMQTT()

mqtt_client.connect()

TOPIC = "Channel 2 Derived Pk"
mqtt_client.subscribe(TOPIC) # use any topic

# Initialize an empty DataFrame
data = pd.DataFrame(columns=["Time", "Value"])

# Define constraints
max_points = 100  # Maximum number of points to keep
y_min, y_max = -3, 3  # Fixed Y-axis range

# Thread lock to prevent race conditions
data_lock = threading.Lock()

# Function to simulate an incoming data stream
def generate_data():
    global data
    last_time = None  # Track last inserted time
    
    while True:
        with data_lock:
            new_time = datetime.datetime.now().astimezone().replace(microsecond=0)  # Use local time and remove microseconds
            
            # Ensure we only add ONE point per second
            if new_time == last_time:
                time.sleep(0.1)  # Short wait to recheck
                continue  
            
            last_time = new_time  # Update last added time

            try:
                payload = mqtt_client.get_latest_payload()
                
                new_value = payload[TOPIC]  # Generate a random value
            except Exception as e:
                continue
                
            # Create new entry            
            new_entry = pd.DataFrame({"Time": [new_time], "Value": [new_value]})

            # Append new data point and enforce max row count
            data = pd.concat([data, new_entry], ignore_index=True).iloc[-max_points:]

            # Print the latest row and correct total row count
            # print(f"Added: {new_entry.iloc[0].to_dict()} | Total Rows: {len(data)}")

        time.sleep(1)  # Wait exactly 1 second before adding the next point

# Start data generation in a separate thread (ONLY ONCE)
if not hasattr(generate_data, "started"):
    threading.Thread(target=generate_data, daemon=True).start()
    generate_data.started = True

# Function to plot data smoothly
def plot_data():
    global data
    while True:
        plt.figure(figsize=(8, 4))
        
        if not data.empty:
            # Define the x-axis window anchored to the current time.
            # This window will always span the last (max_points-1) seconds.
            current_time = datetime.datetime.now().astimezone()
            window = datetime.timedelta(seconds=max_points - 1)
            plt.xlim(current_time - window, current_time)
            plt.ylim(y_min, y_max)
            
            sns.lineplot(x="Time", y="Value", data=data, marker="o", color="b")
            
            # Format x-axis ticks as HH:MM:SS
            plt.xticks(rotation=45)
            ax = plt.gca()
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
        
        plt.xlabel("Time (HH:MM:SS)")
        plt.ylabel("Value")
        plt.title("Real-time Data Stream (Simulated)")
        plt.grid()
        plt.tight_layout()
        
        fig = plt.gcf()
        yield fig  # Yield the updated figure
        
        plt.close(fig)
        time.sleep(1)

# Gradio interface with live updates
iface = gr.Interface(fn=plot_data, inputs=[], outputs="plot", live=True)
iface.launch(share=True)
