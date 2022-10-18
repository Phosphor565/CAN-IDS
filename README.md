# CAN BUS Intrusion Detection System Investigation

This repository contains the data and source code which was produced as part of my penultimate honours project during my studies at the University of Abertay.  

All scripts and programs were developed within an Ubuntu Linux Environment (22.02LTS) software versions are as follows

	- Python 3.10.4
	- GCC (Ubuntu 11.2.0-19ubuntu1) 11.2.0

A requirments.txt has been included which will cover all python3 dependencies within 'scripts' directory

# scripts 

## setup_vcan.sh 
This script automatically sets up the virtual CAN adapter which forms the bases of the test environment for the IDS
and replaying of CAN data. Creation of the new adapter can be confirmed using 'ifconfig' and looking for a new 
adapter named 'vcan0'

## 0_recording 
This directory contains the python scripts that were used to receive and record data from the [nano-can](https://github.com/mintynet/nano-can) device.

### nano_dump.py
This is the script that receives serial data and assigns a timestamp to said data before writing it to a file.
This script was run in a Windows 11 Environment.

### canplayer_format.py
This script takes the log file created by 'nano_dump.py' and reformats it so that it may be replayed by the CAN 
utility 'canplayer'
The format for the messages is as follows
> (TIMESTAMP) VIRTUAL_ADAPTER ID#DATA_PAYLOAD
  

## 1_attack_analysis
This directory contains the python scripts used during the initial CAN data analysis during the development of the
 'can_attack' program.

### CAN_to_SQL.py
Takes a CAN logfile and converts it to an SQLite database for future querying and analysis. 
NOTE: This script can take ~5min to execute

### calculate_attack.py
This script queries the SQLite database to identify the following per CAN ID
- Frequency of CAN messages per second
- An estimate of the interval between CAN messages
- Estimated attack frequency which would constitute a 'successful' attack 

## 2_interval_analysis
This directory has scripts pertaining to the development of the interval IDS

### interval_to_graph.py
During the development there were many false positives using calculated estimated thresholds. 
To debug this, data visualisations were used. This script creates these visualisations.
To variables for choosing the targeted ID and number of intervals that need to be analysed are
found at the top of script with commented instructions. (requires CAN SQLite DB)

## 3_frequency_analysis
This directory has scripts pertaining to the development of the frequency IDS

### calculate_frequency.py
This script calculates the frequency of messages from the recording per CAN ID within 1 second intervals.
This includes,
- Peak frequency observed 
- Lowest frequency observed
- Most frequent frequency observed 

(requires CAN SQLite DB)

## 4_ML_analysis
This directory contains the scripts required to convert the CAN data recording into data which can be processed by 
machine learning algorithms to differentiate between attacks. 

### process_ml_data.py
This script performs two functions which are chosen at runtime

1. Parse CAN recording into 5 separate files which will form the bases of data for the 5 different classes of
data.
	- Normal 
	- DoS attack
	- High frequency injection attack
	- Medium frequency injection attack
	- Low frequency injection attack

2. Once the data has been parsed, instructions are displayed on how to replay the data and create the attack data
sets.

The overall frequency and packet interval is calculated for each second interval of the recordings

NOTE: for convenience the completed machine learning dataset has been included in the file 'CAN_data.csv' 

## 5_data
This directory contains a backup of all the data sources used by the scripts.
	
- CAN_data_recording.log > raw data recording
- can_data.db > SQLite database containing two tables which have details on the recording
- CAN_data.csv > Recording data transformed into ML dataset containing the overall frequency & interval for each 
  1 second interval of the recording. 

# Intrusion Detection Systems

All programs written in C can be compiled with GCC

## 0_attack
This directory holds the program responsible for implementing attacks upon the virtual CAN network

### can_attack.c
This program can be used to inject messages into the virtual CAN adapter. It takes 3 parameters
- ID = The CAN ID of the messages you wish to inject
- Frequency = The number of messages you wish to inject per second
- Duration = The duration of the attack in seconds

Some example commands are shown below,

- High rate injection attack   
> ./can_attack 2F9 1240 5
- Medium rate injection attack 
> ./can_attack 38D 280 5
- Low rate injection attack    
> ./can_attack 7F2 20 5
- DoS attack 		       
> ./can_attack 2F9 1 1

 These attack frequencies are calculated based on the normal frequency for each ID. 

 NOTE: DoS attack has the frequency and duration set to 1. The attack will inject messages at the fastest
 rate possible. The attack will continue until the user exits using CTRL + C

## 1_interval >
This directory contains the implementation for the interval IDS.

### interval_ids_targeted.c
This program can detect injected messages into the virtual CAN adapter when regular data is being replayed to
simulate the normal operating of a vehicle. It does so by reading in a dataset of thresholds from the
'ID_meadian_interval.csv' file. If messages with a specific ID are observed to have intervals shorter than the 
pre-defined interval threshold, an alert will be raised. 

### ID_meadian_interval.csv
Contains the calculated thresholds of time interval for each unique CAN ID. These have been adjusted depending
on the nature of the CAN data for each ID to prevent false positives. 

## 2_frequency
This directory contains the implementation for the frequency IDS

### frequency_ids.c
This program can detect injected messages into the virtual CAN adapter when regular data is being replayed to
simulate the normal operating of a vehicle. It does so by reading in a dataset of the maximum observed 
frequencies of messages per second of each unique ID. If a increase in frequency between each 1 second interval
is observed then an alert will be raised.

### ID_max_frequency.csv
Contains the calculated max frequency observed for each CAN ID.

## 3_machine_learning
This directory contains the scripts used to implement machine learning algorithms to classify CAN attack data. 

### 1_algorithm_comparison.py
This script takes the CAN_data.csv and compares different machine learning models performance to identify suitable 
models for classifying attack data. Produces a box and whisker diagram to display the results as a '%' of accuracy.
The following models are compared,

- Logistic Regression (LR)
- Linear Discriminant Analysis (LDA)
- K-Neighbours Neighbours (KNN)
- Classification and Regression Trees (CART)
- Gaussian Naive Bayes (GNB)

From this the 3 most suited algorithms were tested

### 2_LDA_implementation.py
A script which implements Linear Discriminant Analysis model to classify CAN attack data. Produces, a confusion 
matrix, classification report.

### 3_KNN_implementation.py
A script which implements K-Nearest Neighbour model to classify CAN attack data. Produces, a confusion 
matrix, classification report.

### 4_NB_implementation.py
A script which implements Gaussian Naive Bayes model to classify CAN attack data. Produces, a confusion 
matrix, classification report.

# Image_Artefacts 
This directory contains diagrams and figures which can help explain software functionality and the project as a whole

## 0_simulation_environment.png
Gives an overview of the simple simulation environment which is comprised of the following.
- Virtual CAN adapter (VCAN0)
- Program for injecting data into VCAN0 (developed by me)
- canplayer utility from can-utils (https://github.com/linux-can/can-utils)
- IDS program (developed by me)
![simulation_environment.png](/Image_Artefact/0_simulation_environment.png)

## 1_interval_code_flow_diagram.png
Depicts the coding flow of the intrusion detection segment of the interval IDS implementation.
![interval_code_flow_diagram.png](/Image_Artefact/1_Interval_code_flow_diagram.png)

## 2_Frequency_code_flow_diagram.png
Depicts the coding flow of the intrusion detection segment of the frequency IDS implementation. 
![interval_code_flow_diagram.png](/Image_Artefact/2_Frequency_code_flow_diagram.png)

# Video Artefacts 
This directory contains video demonstrations of the project

## 1_IDS_demo.mp4
This video shows the operation of the 'interval IDS' within 4 terminal panels. Details of which are shown below.

	__________________________________________________________________________________
	|                                        |                                        |
	|                                        |                                        |
	|                                        |                                        |
	|      IDS Program                       |      cansniffer                        |
	|      - Alerts to injected CAN messages |      - Displays CAN data on VCAN0      |
	|                                        |                                        | 
	|                                        |                                        |
	|                                        |                                        |
	|________________________________________|________________________________________|
	|                                        |                                        |
	|                                        |                                        |
	|                                        |                                        |
	|      canplayer                         |       can_attack                       |
	|      - Replays legitimate CAN data     |       - Injects CAN messages           |
	|                                        |                                        |
	|                                        |                                        |
	|                                        |                                        |
	|                                        |                                        |
	|________________________________________|________________________________________|


Things of note that happen during this demo include,

1. Data injected using can_attack overwhelms the virtual CAN network with legitimate
    messages for the ID '2F9' being replaced by the injection data 'DEADBEEF'.
    This is visible immediately in the 'cansniffer' panel when the attack is commenced

2. The IDS alerts to an intrusion displaying the timestamp of said intrusion in addition
	to the offending CAN ID.


The same setup can be used with the Frequency IDS with a similar output 


## 2_ML_demo.mp4
This video shows one of the machine learning scripts in action. It displays its results in the form of a 
Confusion matrix (both graphical and terminal) & a classification report
