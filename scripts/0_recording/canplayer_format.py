'''
Reformats 'nano_dump.py' recording to be replayed with canplayer CAN utility

Author: Phosphor565
Date: 10/5/22
''' 

import sys
from tqdm import tqdm
import re

# Check if correct number of arguments provided
if len(sys.argv) == 2:
    filename = sys.argv[1]
else:
    print("\n\ntoo many arguments passed, use the following format to run this script")
    print("\n$ python3 can_format.py filename.log\n\n")

# Open the file using the filename provided
try:
    f = open(filename, "r")
    data_lines = f.readlines()
except (FileNotFoundError, IOError):
    print("File not found...")


new_filename = filename.replace("CAN_data_", "")
new_filename = "candump-" + new_filename
log = open(new_filename, "w")

for data in tqdm(data_lines, "Parsing Data"):

    # Check if there is message data
    message_data = re.search(r"\[(.*?)\]", data).group(1)
    
    # If blank continue
    if message_data == '':
        continue
    
    # Get ID
    msg_id = message_data[15:18]

    # Get Data
    msg_data = message_data.split("Data:")[1].replace(" 0x", "")

    # Get Time
    msg_time = re.search(r"\((.*?)\)", data).group(1)

    log.write("(" + msg_time + ") vcan0 " + msg_id + "#" + msg_data + "\n")

log.close()

