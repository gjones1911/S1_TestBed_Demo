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
import pytz  # Add this import for timezone handling

from my_mqtt import MyMQTT

try:
    mqtt_client = MyMQTT()

    mqtt_client.connect()

    TOPIC = "Channel 2 Derived Pk"

    mqtt_client.subscribe(TOPIC) # use any topic
except Exception as e:
    print(f"MQTT connection failed: {e}. Retrying in 5 seconds...")
    time.sleep(5)

# Initialize an empty DataFrame
data = pd.DataFrame(columns=["Time", "Value"])

# Define constraints
max_points = 100  # Maximum number of points to keep
# y_min, y_max = -3, 3  # Fixed Y-axis range

# Thread lock to prevent race conditions
data_lock = threading.Lock()

# Function to simulate an incoming data stream
def generate_data():
    global data
    last_time = None  # Track last inserted time
    
    while True:
        with data_lock:
            # Check if the client is connected
            if not mqtt_client.broker_connection_status:
                try:
                    mqtt_client.connect()
                    mqtt_client.subscribe(TOPIC)
                    print("Reconnected to MQTT broker.")
                except Exception as e:
                    # mqtt_client.disconnect()
                    print(f"Disconnecting: {e}. Retrying in 5 seconds...")
                    time.sleep(5)
                    continue  # Skip the rest of the loop and retry

            new_time = datetime.datetime.now(pytz.timezone('US/Eastern')).replace(microsecond=0)  # Use local Eastern time and remove microseconds
            
            # Ensure we only add ONE point per second
            if new_time == last_time:
                time.sleep(0.1)  # Short wait to recheck
                continue  
            
            last_time = new_time  # Update last added time

            try:
                payload = mqtt_client.get_latest_payload()
                
                new_value = float(payload[TOPIC])  # Ensure the value is a double
            except Exception as e:
                # mqtt_client.disconnect()
                new_value = 0  # Set value to 0 if there's an exception
                
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
        plt.style.use('dark_background')  # Set the plot style to dark background
        plt.figure(figsize=(8, 4))
        
        if not data.empty:
            # Convert the 'Time' column to the desired timezone
            data['Time'] = data['Time'].dt.tz_convert('US/Eastern')
            
            # Define the x-axis window anchored to the current time.
            # This window will always span the last (max_points-1) seconds.
            current_time = datetime.datetime.now(pytz.timezone('US/Eastern'))
            window = datetime.timedelta(seconds=(max_points - 1))
            plt.xlim(current_time - window, current_time)
            # plt.ylim(y_min, y_max)
            
            sns.lineplot(x="Time", y="Value", data=data, marker="o", color="darkorange")
            
            # Format x-axis ticks as HH:MM:SS
            plt.xticks(rotation=45)
            ax = plt.gca()
            # Convert the datetime to local time before formatting
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S", tz=pytz.timezone('US/Eastern')))
        
        plt.xlabel("Eastern Time (HH:MM:SS)")
        plt.ylabel(TOPIC) # value
        plt.title("S1 Testbed Real-time Data Streaming)")
        plt.grid()
        plt.tight_layout()
        
        fig = plt.gcf()
        yield fig  # Yield the updated figure
        
        plt.close(fig)
        time.sleep(1)

# Gradio interface with live updates
iface = gr.Interface(fn=plot_data, inputs=[], outputs="plot", live=True)
iface.launch(share=True)
