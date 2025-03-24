# Code Folder for S1_TestBed_Demo

> Contains several files and modules for running the S1-testbed Digital Twin demo

## Demo-Usage

> To start the demo you just have to ensure your virtual environment is active (see README.md in root folder), you are in a command line inside of the code folder and then use the following command:
```bash
source s1_demo_starter.sh
```
> The script will print out the progress of starting up each component and it will take a minute or two for everything to get going. If all goes well you will be able to see output from each script in the indicated .log file in the logs folder. 


## Folders:

* [logs](./logs)
  * contains text files for debugging, viewing the three main mqtt scripts (see below scripts purposes sections)
* [RandomForestModel](./RandomForestModel)
  * contains a set of trained random forest models for s1 motor state prediction and python scripts to train/generate them.
* [RandomForestPredictionMQTT](./RandomForestPredictionMQTT)
  * contains modules and scripts for the generation of a s1 motor state based on data broadcast by the S
* [S1_Data_MQTT](./S1_Data_MQTT)
  * contains the modules and script that will begin the broadcasting of s1 data from the opcua connection onto a mqtt connection

* [s1_mqtt_instructor](./s1_mqtt_instructor)
  * contains modules, classes, models, and scripts used to facilitate AI based generation of s1 motor fault correction. 
  * ***Important***: to work a version of the "S1_MotorMaintenaceInstructor" LLM must be in the s1_mqtt_instructor.


* [S1_MotorMaintenaceInstructor](./S1_MotorMaintenaceInstructor)
  * the LLM model used to generate instructions (will not be in the git due to size)
  * can be downloaded from:  


* [LLM_TOOLS](./LLM_TOOLS)
  * contains the class the connects to and operates the S1_MotorMaintenanceInstructor bot

# main scripts

* [RandomForestPredictionMQTT/S1Predict.py](./RandomForestPredictionMQTT/S1Predict.py)
  * starts the process of predicting motor states based on data broadcast over the mqtt broker
  * **Important**:

* [S1_Data_MQTT/S1Data_MQTT_Pub.py](./S1_Data_MQTT/S1Data_MQTT_Pub.py)
  * begins pulling data from the S1 using a opcua connection and publishing on the mqtt connection

* [s1_mqtt_instructor/s1_instruction_starter.py](./s1_mqtt_instructor/s1_instruction_starter.py)
  * can be run from the command line to start the Instruction Component of the S1-DT-Demo
  * assumes the connection is sending predictions on the topic "prediction"
  * usage:
    * ```python
      python3 s1_instruction_starter.py
      ```
## Status code decoding

> The below numeric to string mappings help indicate what state the motor is predicted to be in. 
  Using the value indicated you can look up what it is predicting.


## new fault set (2/24/25)
* 0: "baseline"
* 1: "bent_shaft"
* 2: "eccentric_rotor"
* 3: "offset_misalignment"
* 4: "imbalance"  **
* 5: "faulted_coupling"
* 6: "angular_misalignment"



## Old set

* 0: "baseline"
* 1: "bent_shaft"
* 2: "eccentric_rotor"
* 3: "offset_misalignment"
* 4: "resonance_beam" (Remove)
* 5: "imbalance"  **
* 6: "faulted_coupling"
* 7: "faulted_bearing" (Remove)
* 8: "angular_misalignment"
* 9: "looseness" (Remove)