'''
Script which takes a CAN recording and creates a SQLite DB for future analysis

Resulting DB will include 2 tables
 	- CAN_data = a full list of the recieved can data with ID, DATA payload & Timestamp
	- CAN_id = a list of all the unique CAN ID seen & how often they appear in the recording

Author: Phosphor565
Date: 10/5/22
'''
import sqlite3
from tqdm import tqdm

# Set target CAN recording file here (must be in 'candump format')
target_file = "CAN_data_recording.log"

# Generates database file
def gen_db():
    # create database + make cursor object (to edit)
    connection = sqlite3.connect('can_data.db')
    cursor = connection.cursor()

    # Make ID table
    cursor.execute('''CREATE TABLE IF NOT EXISTS CAN_id
                    (ID TEXT, occurrence_count INT)''')
    connection.commit()

    #Make Data Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS CAN_data
                    (ID TEXT, data_value TEXT, time_value TEXT)''')
    connection.commit()
    
    # Close Connection
    connection.close()


# Process log file + insert them into DB
def process_data(log_data):
    # connect database + make cursor object (to edit)
    connection = sqlite3.connect('can_data.db')
    cursor = connection.cursor()

    for data in tqdm(log_data, desc ="Filling CAN_data table"):
        # Parse line to get ID, Data value & Time value
        time_value = data[1:18]
        data = data.split(' ')
        data = data[2]
        id_value = data[0 : 3]
        data = data.split('#')
        data_value = data[1]

        # Craft query + grab data values
        insert_query = """INSERT INTO CAN_data(ID, data_value, time_value)
                        VALUES
                        (?,?,?)"""
        insert_data = (id_value, data_value, time_value)

        cursor.execute(insert_query, insert_data)
        connection.commit()

    connection.close()


# Read log and return a list of the lines
def read_log():
    global target_file
    # Read in log file and convert lines into a list
    f = open(target_file, "r")
    data_lines = f.readlines()

    return data_lines

# Process ID_data 
def process_id(id_data):
    # connect database + make cursor object (to edit)
    connection = sqlite3.connect('can_data.db')
    cursor = connection.cursor()

    for id in tqdm(id_data, desc ="Filling CAN_id table  "):
        cursor.execute("SELECT ID FROM CAN_id WHERE ID = ?", (id,))
        db_data = cursor.fetchall()

        # For first occurrance of ID
        if len(db_data) == 0:
            insert_query = """INSERT INTO CAN_id (ID, occurrence_count)
                            VALUES
                            (?, ?)"""
            insert_data = (id, 1)
            cursor.execute(insert_query, insert_data)
            connection.commit()
        # If ID exists increase occurance by 1
        else:
            update_query = """UPDATE CAN_id SET occurrence_count = occurrence_count + 1 WHERE ID = ?"""
            cursor.execute(update_query, (id,))
            connection.commit()
    
    connection.close()
    print("\n")
            


# Parse the IDs from the log + pass the parsed data for processing
def parse_id(data):

    id_list = []
    # split the data and then grab the 3 characters responsible for CAN ID
    for x in data:
        x = x.split(' ')
        x = x[2]
        x = x[0 : 3]
        id_list.append(x)
    
   
    process_id(id_list)
    
    


def main():
    gen_db()
    log_data = read_log()
    print("Processing CAN Log Data, this may take some time..\n")
    parse_id(log_data)
    process_data(log_data)
    print("\nProcessing log complete, database ready for review\n")

if __name__ == "__main__":
    main()
