#!/bin/bash

# This script is intended to be run in the S1_TESTBED_DEMO/code folder. It will start the python environment 
# expected to run the S1 demo scripts. The script assumes there is a folder in the root directory containing 
# a python virtual environment labeled 's1demovenv' that has the installations listed in the requirements.txt 
# file found in the code directory. 

# activate the expected environment
source ../venvs/s1demovenv/Scripts/activate

echo "The S1 demo python virtual environment (s1demovvenv) has been activated!!!"
