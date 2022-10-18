'''
This script performs the following actions,
1 - Parse data from 'CAN_data_recording.log' into 5 equal portions
2 - Parse processed data into machine learning data

Note:
When re-recording rename candump log giles to the file names displayed below in 'file_names' list

Author: Phosphor565
Date: 10/5/22
'''
import os
import numpy

file_names = ['1_normal_data.log', '2_low_attack_data.log', '3_med_attack_data.log', '4_high_attack_data.log', '5_DoS_attack_data.log']
attack_dir_name = "attack_data"
processed_dir_name = "processed_data"

# _____________________________________________________________________________________

# Creates the directories to store data
def create_directories(attack, processed):
    try:
        os.mkdir(attack)
        os.mkdir(processed)
    except FileExistsError:
        print("\n\nDirectories exist, delete and try again")

# Parses data line to obtain timestamp
def get_timestamp(data_line):
    timestamp = float(data_line[data_line.find("(")+1:data_line.find(")")])

    return timestamp

# write file
def write_file(data_list, directory, filename):

    if directory:
        filename = f"{directory}/{filename}"
    else:
        filename = filename

    file = open(filename, "w")

    for x in data_list:
        file.write(x)
    
    file.close()

# Calculates the mean interval and frequency of a second of data
def calculate_metrics(time_lists):

    interval_list = []

    for x in range(len(time_lists)):
        if x == (len(time_lists) - 1):break
        difference = time_lists[x+1] - time_lists[x]

        interval_list.append(difference)
    
    point_interval_mean = numpy.mean(interval_list)
    frequency = len(time_lists)

    return point_interval_mean, frequency


# _____________________________________________________________________________________

# create dataset > creates the ML dataset using the processed recording data in 'processed_data' dir
def create_dataset():
    global processed_dir_name

    # get directory listing of target directory
    # order should be normal > low > med > high > dos 
    dir_list = os.listdir(processed_dir_name + "/")
    dir_list.sort()

    # Declare classifications/ log file type
    log_type = ['normal', 'low', 'med', 'high', 'DoS']

    # List for storing ml dataset
    ml_data_list = []

    for x in range(len(log_type)):
        # Read log file
        file_name = processed_dir_name + "/" + dir_list[x]
        log_file = open(file_name, "r")
        log_file = log_file.readlines()

        # Keep track of iterations (55 = 55 seconds processed) + get starting timestamp for logfile
        iteration = 0
        start_time = get_timestamp(log_file[0])

        while iteration < 55:
            # Calculate end time + declare list for all data points within second interval
            end_time = start_time + 1
            second_list = []
            
            # For each line in current log file see what is within this second interval
            for line in log_file:
                timestamp = get_timestamp(line)
                if(timestamp >= start_time) and (timestamp <= end_time):
                    second_list.append(timestamp)
            
            # calculate average interval and the frequency of messages from the 1 second interval
            interval, frequency = calculate_metrics(second_list)

            # format into CSV entry with classification based on which log file is being processed
            entry = f"{interval},{frequency},{log_type[x]}\n"
            ml_data_list.append(entry)

            # set start_time to end_time to move to next secon increment + increase increment by 1
            start_time = end_time
            iteration+=1
        
    # WRITE TO FILE ?
    write_file(ml_data_list, "", "CAN_data.csv")

    print("\n\nDataset written to file 'CAN_data.csv'\n")

#  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -

 # Process data function > creates directories and splits CAN data into 5 equal 55 second logs           
def process_data():
    global file_names
    global attack_dir_name
    global processed_dir_name
    print("\n\nProcessing data")
    print("- Attack data will be placed into the 'attack_data' directory")
    print("- Processed data will be placed into 'processed_data' directory")

    # Create directories
    #create_directories(attack_dir_name, processed_dir_name)

    # Load CAN_data_recording.log file
    CAN_data = open("CAN_data_recording.log", "r")
    CAN_data = CAN_data.readlines()

    # Get start time
    start_time = get_timestamp(CAN_data[0])

    # Iterate through filenames
    for name in file_names:

        # List to hold file data + calculate end time (increments of 55 seconds)
        file_data = []
        end_time = start_time + 55

        # Iterate through CAN_data file to find entries that are within 55 second increment
        for data_line in CAN_data:
 
            timestamp = get_timestamp(data_line)

            if (timestamp >= start_time) and (timestamp <= end_time):
                file_data.append(data_line)

        # If file is for 'normal' data store in processed dir
        # else store in attack data dir to be processed
        if "normal" in name:
            write_file(file_data, processed_dir_name, name)
        else:
            write_file(file_data, attack_dir_name, name)
        
        # Set start to end time to move to next 55 second increment 
        start_time = end_time
    
    # Display instructions on what to do next
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    print("\n\n< Data written >\n")
    print("Data in 'attack_data' directory must be replayed & re-recorded whilst an attack is being conducted")
    print("using the 'candump' utility\n")
    print("The following message can be appended to the start and end of each 'attack_data' file")
    print("\n        - (start/end timestamp) vcan0 123#636F66666565\n")
    print("To signify start and end of recording so it can be trimmed after replay")
    print("\n the following commands can be used with 'can_attack' to perform different levels of attack")
    print("     Low injection attack = ./can_attack 7F2 20 65")
    print("     Med injection attack = ./can_attack 38D 280 65")
    print("    High injection attack = ./can_attack 2F9 1240 65")
    print("               DoS attack = ./can_attack 7F2 1 1")
    print("\nonce recorded, recordings can be trimmed and renamed and stored in 'processed_data' directory")
    print("Run option 2 on this script to convert this data to a machine learning dataset\n")


# _____________________________________________________________________________________
# Main function
def main():
    print("'process_ml_data.py > process recording data into ML dataset'")
    print("Make a selection")
    print("1 - Seperate recording into 5 equal parts")
    print("2 - Parse processed data into machine learning dataset")
    choice = int(input("> "))

    if choice == 1:
        process_data()
    else:
        create_dataset()
        


if __name__ == "__main__":
    main()
