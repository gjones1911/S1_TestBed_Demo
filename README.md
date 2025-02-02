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
