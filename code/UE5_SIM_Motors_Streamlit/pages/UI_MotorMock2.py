import streamlit as st
import pandas as pd
import paho.mqtt.client as mqtt
import time
import os
from threading import Thread, Event

# Hive MQTT Broker
mqttBroker = 'recoil.ise.utk.edu'

# Streamlit App
st.title('MQTT Publisher with Dynamic State')

# Define the mapping from strings to integers
state_mapping = {
    'Baseline': 0,
    'Bent Shaft': 1,
    'Eccentric Rotor': 2,
    'Offset Misalignment': 3,
    'Resonance Beam': 4,
    'Imbalance': 5,
    'Faulted Coupling': 6,
    'Faulted Bearings': 7,
    'Angular Misalignment': 8,
    'Looseness': 9
}


# Create a list of strings for the select box
state_options = list(state_mapping.keys())

# Initialize session state for current state and stop event
if 'Motor2_current_state' not in st.session_state:
    st.session_state.Motor2_current_state = None
if 'Motor2_stop_event' not in st.session_state:
    st.session_state.Motor2_stop_event = Event()

# User input for state using a select box
selected_state = st.selectbox('Select State Value', state_options, index = state_options.index(st.session_state.Motor2_current_state) if st.session_state.Motor2_current_state in state_options else 0)

# Map the selected state to its corresponding integer
new_state = state_mapping[selected_state]

# Show the selected state value
st.write(f'Current State: {selected_state} (Mapped to: {new_state})')

def publish_data(state, stop_event):
    client = mqtt.Client('MotorMock2_UI')
    client.username_pw_set(username = 'hivemquser', password = 'mqAccess2024REC')
    client.connect(mqttBroker)
    client.loop_start()

    # Define paths and load data
    project_path = os.getcwd()
    data_path = os.path.join(project_path, 'data')
    csv_file = os.path.join(data_path, 'ALL_S1_DATA_INT.csv')
    df_temp = pd.read_csv(csv_file, chunksize = 50000)
    df = pd.concat(df_temp)

    data_cols = df.columns

    filtered_df = df[df['status'] == state]

    for index, row in filtered_df.iterrows():
        if stop_event.is_set():
            break
        str_feat = ''
        for feature in data_cols:
            client.publish('Motor2/' + feature.strip(), row[feature], qos=1)
            str_feat += f'{row[feature]},'
        time.sleep(1)  # Adjust the interval as needed

    client.loop_stop()
    client.disconnect()

# Handle the state change
if selected_state != st.session_state.Motor2_current_state:
    st.session_state.Motor2_current_state = selected_state
    st.session_state.Motor2_stop_event.set()  # Signal to stop the previous thread

    # Wait for the previous thread to finish
    if 'Motor2_publish_thread' in st.session_state:
        st.session_state.Motor2_publish_thread.join()
    
    st.session_state.Motor2_stop_event.clear()  # Reset the stop event
    st.write(f'Starting to publish data for state: {selected_state}')
    Motor2_publish_thread = Thread(target = publish_data, args = (new_state, st.session_state.Motor2_stop_event))
    st.session_state.publish_thread = Motor2_publish_thread
    Motor2_publish_thread.start()
else:
    if st.button('Publish Data'):
        st.write('Publishing data for current state:', selected_state)
        publish_data(new_state, st.session_state.Motor2_stop_event)
