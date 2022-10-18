'''
Script to recieve serial data from 'Nano-CAN' and record it with appropriate timestamps

Author: Phosphor565
Date: 10/5/22
''' 

import serial
import time
import os
from datetime import datetime

# initalise serial device + get set filename
ser = serial.Serial('COM4', 500000, rtscts=1)
now = datetime.now()
date_time = now.strftime("%d-%m-%Y_%H%M%S")
filename = f'CAN_data_{date_time}.log'

print("Recording Data, press CTRL + C to finish recording and write to file")

recording_Data = []

# Record data into a list
try:
     while True:
            ser.flushOutput()# changed from 'flush' test and maybe remove
            data = ser.readline().decode('utf-8').rstrip()
            timestamp = '%.6f' % time.time()
            recording_Data.append(f'({timestamp}) [{data}]\n')

# When keyboard interrupt recieved, write data recording to file
except KeyboardInterrupt:
    print("\nWriting to file...\n")
    with open(filename, 'w') as file:
        for dataline in recording_Data:
            file.write(dataline)
        file.close()
    print(f'\nRecoding written to "{filename}"')
    print("Exiting....")

except UnicodeDecodeError:
    print("\nUnicode Decode Error during recording, try again\n")
    os.remove(filename)
