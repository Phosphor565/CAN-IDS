'''
This script queries an SQLite database which contains CAN data to identify the following metrics per CAN ID

     - Estimated normal Frequency per second
     - Estimated interval threashold in microseconds
     - Estimated attack frequency for simulated successful attack

Author: Phosphor565
Date: 10/5/22
'''

import sqlite3
import numpy

# Connect to database and get a list of IDs
con = sqlite3.connect('can_data.db')
cur = con.cursor()
cur.execute("SELECT ID FROM CAN_id ORDER BY occurrence_count DESC")
fetched_id = cur.fetchall()
id_list = []
for id in fetched_id:
    id_list.append(id[0])

start_time = 1649856600
end_time = 1649856880

iterations = end_time - start_time

print("'get_frequency.py'\n")
print("Script will print the following for each unique CAN ID")
print("     - ID")
print("     - Estimated normal Frequency per second")
print("     - Estimated interval threashold in microseconds")
print("     - Estimated attack frequency for simulated successful attack\n")
print("_________________________________________")

for id in id_list:
    frequency_list = []
    for x in range(iterations):
        current_time = (start_time + x)
        current_time_query = str(current_time) + "%"
        cur.execute("SELECT COUNT(*) FROM CAN_data WHERE ID = ? AND time_value like ?", (id, current_time_query))
        fetched_id = cur.fetchall()
        frequency_list.append(fetched_id[0][0])

    mean_result = round(numpy.mean(frequency_list))

    if mean_result == 0:
        mean_result = 1

    attack_result = mean_result * 20
    threshold = round(1000000 / mean_result)

    print(f"ID = {id}")
    print(f"Normal Frequency    = {mean_result} messages/s")
    print(f"Interval Threashold = {threshold} μs")
    print(f"Attack Frequency    = {attack_result} messages/s")
    print("_________________________________________")
