'''
A script to display a graph which shows the intervals of a specific CAN id 
Displays the intervals for a specific ID in the recording as a graph

Author: Phosphor565
Date: 10/5/22
'''
import sqlite3
import matplotlib.pyplot as plt

# Select targeted CAN ID + Set number of intervals you wish to analyse
# Set interval = "" to get all available intervals for that ID
target_id = "2F9"
no_intervals = "50"

# ______________________________________________________________________

# Connect to database and get a list of IDs
con = sqlite3.connect('can_data.db')
cur = con.cursor()

# Change query depending on what is set
if not no_intervals:
    cur.execute("SELECT time_value FROM CAN_data WHERE ID = ?",(target_id ,))
else:
    cur.execute("SELECT time_value FROM CAN_data WHERE ID = ? LIMIT ?",(target_id , no_intervals))

rows = cur.fetchall()

# Make a list of the fetched times
packet_times = []
for row in rows:
    packet_times.append(row[0])

# Make a list of the differences between times
packet_intervals = []
for x in range(len(packet_times)):
    if x < len(packet_times) - 1:
        difference = float(packet_times[x + 1]) - float(packet_times[x])
        packet_intervals.append(difference)

# calculate number of intervals
interval_count = []

for x in range(len(packet_intervals)):
    interval_count.append(x)

# plotting the points
plt.plot(interval_count, packet_intervals, label="Interval")
 
# naming the x axis
plt.xlabel('x - Interval Count')
# naming the y axis
plt.ylabel('y - Time Interval (sec)')
 
# giving a title to my graph
if not no_intervals:
    plt.title(f'All intervals for ID: {target_id}')
else:
    plt.title(f'First {no_intervals} intervals, for ID: {target_id}')
 
# function to show the plot
plt.legend()
plt.show()

