'''
This script is used to get the following frequency metric per CAN ID

     - Peak frequency identified in CAN messages per second
     - Lowest frequency identified in CAN messages per second
     - Most frequent frequency identified in CAN messages per second

Author: Phosphor565
Date: 10/5/22
'''
import sqlite3

start_time = 1649856600
end_time = 1649856880

# Get list of IDS 
con = sqlite3.connect('can_data.db')
cur = con.cursor()
cur.execute("SELECT ID FROM CAN_id ORDER BY occurrence_count DESC")
fetched_id = cur.fetchall()
id_list = []
for id in fetched_id:
    id_list.append(id[0])

# Calculate second
iterations = end_time - start_time

results = []

def most_frequent(List):
    counter = 0
    num = List[0]
     
    for i in List:
        curr_frequency = List.count(i)
        if(curr_frequency> counter):
            counter = curr_frequency
            num = i
 
    return num

print("'get_frequency.py'\n")
print("This script gets thhe following values")
print("     - ID")
print("     - Peak frequency identified in CAN messages per second")
print("     - Most frequent frequency identified in CAN messages per second\n")

print("__________________________________________________")

for id in id_list:
    frequency_list = []
    for x in range(iterations):
        time_iteration = start_time + x
        current_time_query = str(time_iteration) + "%"
        cur.execute("SELECT COUNT(*) FROM CAN_data WHERE ID = ? AND time_value like ?", (id, current_time_query))
        fetched_id = cur.fetchall()
        frequency_list.append(fetched_id[0][0])

    print(f"ID = {id}")
    print(f"Max frequency       = {max(frequency_list)} messages/s")
    print(f"Min frequency       = {min(frequency_list)} messages/s")
    print(f"Most frequent value = {most_frequent(frequency_list)} messages/s")
    print("__________________________________________________")

