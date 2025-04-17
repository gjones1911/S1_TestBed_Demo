# S1_TestBed_Demo
This repo is for running and maintaining the the S1-testbed demo for the Applied Systems Lab (ASL) at the University of Tennessee, Knoxville. The project is used to support the operation of a S1-testbed Digital Twin demonstration that allows users to run the three scripts needed to push the data across the mqtt connection for visualization and animation purposes in the AR/VR unity environment. The project allows for the two way control of the physical and digital versions of the motor in both in terms of RPM as well as visualizations in the VR/AR space of the current state of the machine.


# Folders:

* [code](./code)
  * all code and scripts used to run/maintain the demo
* [data](./data)
  * any relevant data files
* [slides](./slides)
  * any relevant slides and presentations
* [latex](./latex)
  * any relevant overleaf project links


# Usage

## Set up
* clone the repo found here: [S1_TESTBED_DEMO](https://github.com/gjones1911/S1_TestBed_Demo)
* inside the root folder create a new virtual environment folder and a new environment. You can change the name of 's1demoenv' to what ever you want, but avoid adding dashes, spaces, and underscores
  * make a folder to hold you venv
    * ```bash
      mkdir venvs
      ```
  * make the new environment
    * ```bash
      python venv venvs/s1demoenv
      ```
  * start your environment on windows
    * ```bash
      source venvs/s1demoenv/Scripts/activate
      ```
  * or, start your environment on linux style environment
    * ```bash
      source venvs/s1demoenv/bin/activate
      ```
  * Install the required modules using the requirements file in the code folder
    * ```bash
      python -m pip install -r code/requirements.txt
      ```

## Usage:
* To start the demo, change directories to the /code folder and follow the instructions for "Demo-Usage" in the [README](./code/README.md) found there. 

# UI features

- Gradio
  - less control: 
- Streamlit
- Flask -> html/css
- Quasar
  - 

## A UI to start / stop the demo

- [x] Subscribe to MQTT (to OPCUA Server) so that we can | XL
  - see the incoming data -> we know it is running! It is ON
    - when it is first ON, we can email / notify people
  - OFF
    - ...
  - timestamps
  - History | log
  - Log viewers

- Visualization of "raw" data -> enduser:: manager, operator, dev, ... | JW+XL
  - time line plots
    - for each feature
  - Historic data
    - v1
  - Live view
    - v2
  - basic stats:
    - Avg, Std, ... window-size
    - Trend line?
  - Download as CSV, XLSX  
  - Live camera 
  - 3D model "live" view
    - Unreal
    - Unity?

- RF Predictor -> end users: engineers, managers,  | JW/GJ
  - confusion matrix?
  - "F1" / confidence (?) / accuracy?
  - two tabs
    - one for ml 
      - model number, version
        - rf:1.0.2
        - lstm:1.5.3 (future) 

    - one for layman

  - what's failure mode?
    - meaning - related docs
      - a graph? (example graph)
      - references? 
  - 

- LLM instructor? | GJ
  - two versions
    - LIVE
    - mockup - simulate a failure
      - "fake" a mqtt message with the failure
  - Text completion
    - given "bent shaft", show the proper instructions 
    - Conversational bot:
      - machine's maintenance history, work orders, crews ....  ! (not s1 yet)
      

- MagicLeap | JLW
  - ML model will be on the S1 server
  - 3D model on the glasses during runtime
  - 3D model / build 
    - ORETTC source code
    - source code on the ASL Workstation 
  - The glass connects to the MQTT / S1 Server during runtime  (?)
  - S1 router
    - S1 Server (OPCUA)
      - MQTT Broker (?local one ?) via a docker
    - S1-2300 | DAQ
    - MagicLeap
    - Industrial Controller



- RF backend UI? Admin's console?
  - how the flow to update the model?
  - when to re-train the model
  - ?

# Workflow

## If docker is not running:

- Step 1: start WSL
  - open `cmd` and type `wsl -d Ubuntu` # it is v24.04
- Step 2: open docker. It should not throw out the "WSL error". 
  - Just a note, we did use /Resources/WSL Integration/`Ubuntu`

## run two scripts to demo
- #1: the main script for ML models
  - under the github project folder: `cd code`, `./s1_demo_starter.sh`
- #2: the mqtt, if the containers are not running in docker
  - under the github project folder: 
    -`cd Demo_Users/XL/Grafana_Suite`
    -`docker compose -f docker-compose.s1.yml up -d`


