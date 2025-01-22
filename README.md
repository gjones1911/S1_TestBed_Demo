# S1_TestBed_Demo
This repo is for the S1-testbed demo for the Applied Systems Lab (ASL) at the University of Tennessee, Knoxville. The project is used to support the operation of a S1-testbed Digital Twin demo. The project allows for the two way control of the physical and digital versions of the motor in both digital-->physical and physical--> digital operations.


# Folders:

* [LLM_TOOLS](/LLM_TOOLS)
  * contains the class the connects to and operates the S1_MotorMaintenanceInstructor bot
* [S1_MotorMaintenaceInstructor](/S1_MotorMaintenaceInstructor)
  * the LLM model used to generate instructions (will not be in the git due to size)
  * can be downloaded from:  

# scripts and purpose

* s1_instruction_utils.py
  * contains functions and variables to support the s1_instruction_utils.py script
 
* s1_instruction_starter.py
  * can be run from the command line to start the Instruction Component of the S1-DT-Demo
  * assumes the connectin is sending predictions on the topic "prediction"
  * usage:
    * ```python
      python3 s1_instruction_starter
      ```