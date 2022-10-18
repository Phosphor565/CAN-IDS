/*
interval_ids
This program demonstrates how the the interval between CAN messages can be used to identify intrusions

Author: Phosphor565
Date: 10/5/22
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <string.h>
#include <stdbool.h>

#include <net/if.h>
#include <sys/ioctl.h>
#include <sys/socket.h>

#include <linux/can.h>
#include <linux/can/raw.h>

#define MAXCHAR 20
#define ALERT_THRESHOLD 10
#define NUMBER_OF_CAN 38

// struct to hold the details of a unique can message
struct can_message{
    int id;
    char hex_id[3];
    int threshold;
    unsigned long last_time;
    int alert_count;
};

/**
 * @brief convertHex()
 * This function takes the string hex argument (for CAN ID) and converts it to 
 * a decimal for transmission over the virual CAN bus. 
 * 
 * @param hex 
 * @return int 
 */
int convertHex(char hex[MAXCHAR]){

    long long base = 1;
    int i = 0, value, length;
    int decimal = 0; 

    length = strlen(hex);
    for(i = length--; i >= 0; i--)
    {
        if(hex[i] >= '0' && hex[i] <= '9')
        {
            decimal += (hex[i] - 48) * base;
            base *= 16;
        }
        else if(hex[i] >= 'A' && hex[i] <= 'F')
        {
            decimal += (hex[i] - 55) * base;
            base *= 16;
        }
        else if(hex[i] >= 'a' && hex[i] <= 'f')
        {
            decimal += (hex[i] - 87) * base;
            base *= 16;
        }
    }

    return decimal;

}// END convertHex -------------------------------------------------------------

/**
 * @brief getTime()
 * Gets the current time in microseconds
 * 
 * @return unsigned long 
 */
unsigned long getTime(){
    struct timeval tv;
    unsigned long time_in_micros;

    gettimeofday(&tv,NULL);
    time_in_micros = 1000000 * tv.tv_sec + tv.tv_usec;

    return time_in_micros;

}

int main(int argc, char **argv)
{   
    // READ CONFIG FILE ________________________________________________________________________
    FILE *fp;
    char row[MAXCHAR];
    char *token;

    int count = 0, iteration = 0, current_id = 0;

    struct can_message can_message_list[NUMBER_OF_CAN];

    // Holds read in values
    int id[NUMBER_OF_CAN];
    int threshold[NUMBER_OF_CAN];

    fp = fopen("ID_median_interval.csv", "r");

    // While there is data from file
    while (iteration < NUMBER_OF_CAN){

        fgets(row, MAXCHAR, fp);
        token = strtok(row, ",");

        // While token is not null
        while(token != NULL){   
            // Assign to one of two arrays depending on count
            // 0 = ID array
            // 1 = Threshold array
            if(count == 0){
                strcpy(can_message_list[iteration].hex_id, token);
                current_id = convertHex(token);
                id[iteration] = current_id;
                token = strtok(NULL, ",");
                count++;
            }
            else{
                threshold[iteration] = atoi(token);
                token = strtok(NULL, ",");
                count = 0;
            }
        }
        // Increase iteration
        iteration++;
    }// Completed reading file


    // Create array of structs to hold data

    for(int x = 0; x < NUMBER_OF_CAN; x++){

        can_message_list[x].id = id[x];
        can_message_list[x].threshold = threshold[x];
        can_message_list[x].last_time = 0;
        can_message_list[x].alert_count = 0;

    }
    // END READ CONFIG FILE ___________________________________________________________________

    // START CAN SETUP ________________________________________________________________________
    int s, i; 
	int nbytes;
	struct sockaddr_can addr;
	struct ifreq ifr;
	struct can_frame frame;

    int running = 1, alert_count = 0;
    unsigned long current_time = 0, difference = 0; 

	printf("Interval IDS Demo\r\n");
    
    // Bind to virual CAN socket
	if ((s = socket(PF_CAN, SOCK_RAW, CAN_RAW)) < 0) {
		perror("Socket");
		return 1;
	}
	strcpy(ifr.ifr_name, "vcan0" );
	ioctl(s, SIOCGIFINDEX, &ifr);
	memset(&addr, 0, sizeof(addr));
	addr.can_family = AF_CAN;
	addr.can_ifindex = ifr.ifr_ifindex;
	if (bind(s, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
		perror("Bind");
		return 1;
	}

    // Stores the recieved numerical CAN ID
    int recieved_id = 0;
    
    // Loop for listening to CAN packets _________________________________________
    while (running){
        nbytes = read(s, &frame, sizeof(struct can_frame));

        recieved_id = frame.can_id;

        current_time = getTime();

        // For loop to iterat through all the known CAN IDs
        for(int x = 0; x < NUMBER_OF_CAN; x++){

            if(can_message_list[x].id != recieved_id) continue;
            
            // Check if last time has been set + calculate difference + set current time as last time
            if(can_message_list[x].last_time != 0){
                difference = current_time - can_message_list[x].last_time;
                can_message_list[x].last_time = current_time;
                
            }
            else{
                can_message_list[x].last_time = current_time;
            }

            // If the difference is below the threshold increase alert count
            if(difference < can_message_list[x].threshold){
                can_message_list[x].alert_count++;
            }
            else{
                can_message_list[x].alert_count = 0;
                break;
            }
            // Alert if recieved message alerts is over threshold
            if(can_message_list[x].alert_count > ALERT_THRESHOLD){
                printf("\nALERT\n");
                printf("ID = %s\n", can_message_list[x].hex_id);
                printf("Alert Time - %lu\n\n", current_time);
                return 0;
            }
            break;

        }// END for loop

    
    
        
    }// END While Loop __________________________________________________________
    

    // Check for close 
	if (close(s) < 0) {
		perror("Close");
		return 1;
	}
	return 0;
}
