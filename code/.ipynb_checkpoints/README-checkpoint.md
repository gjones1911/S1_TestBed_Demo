# Code Folder for S1_TestBed_Demo

> Contains several files and modules for running the S1-testbed Digital Twin demo

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
