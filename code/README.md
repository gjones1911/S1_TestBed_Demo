# Code Folder for S1_TestBed_Demo

> Contains several files and modules for running the S1-testbed Digital Twin demo
* []()
  * .
# Folders:
* [logs](/logs)
  * contains text files for debugging, viewing the three main mqtt scripts (see below scripts purposes sections)
* [RandomForestModel](/RandomForestModel)
  * contains a set of trained random forest models for s1 motor state prediction and python scripts to train/generate them.
* [RandomForestPredictionMQTT]()
  * contains modules and scripts for the generation of a s1 motor state based on data broadcast by the S
* [S1_Data_MQTT](/S1_Data_MQTT)
  * contains the modules and script that will begin the broadcasting of s1 data from the opcua connection onto a mqtt connection


* [s1_mqtt_instructor](/s1_mqtt_instructor)
  * contains modules, classes, models, and scripts used to facilitate AI based generation of s1 motor fault correction. 


* [S1_MotorMaintenaceInstructor](/S1_MotorMaintenaceInstructor)
  * the LLM model used to generate instructions (will not be in the git due to size)
  * can be downloaded from:  


* [LLM_TOOLS](/LLM_TOOLS)
  * contains the class the connects to and operates the S1_MotorMaintenanceInstructor bot

# scripts and purpose

* RandomForestPredictionMQTT/S1Predict.py
  * starts the process of predicting motor states based on data broadcast over the mqtt broker
 
* s1_instruction_starter.py
  * can be run from the command line to start the Instruction Component of the S1-DT-Demo
  * assumes the connection is sending predictions on the topic "prediction"
  * usage:
    * ```python
      python3 s1_instruction_starter.py
      ```
## status code decoding:
* 0: "baseline"
* 1: "bent_shaft"
* 2: "eccentric_rotor"
* 3: "offset_misalignment"
* 4: "resonance_beam"
* 5: "imbalance"
* 6: "faulted_coupling"
* 7: "faulted_bearing"
* 8: "angular_misalignment"
* 9: "looseness"