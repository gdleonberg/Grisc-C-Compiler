#define PACKET_SIZE 512
#define PROGNAME "tftp.g"
#define AF_INET 0
#define SOCK_DRAM 0
#define INADDR_ANY 0
#define RRQ 0
#define DATA 0
#define ACK 0
#define SEEK_CUR 0
#define ERROR 0
#define FILENOTFOUND 0

typedef struct FILE FILE;
struct FILE
{
    int handle;
};

typedef struct reqPacket reqPacket;
struct reqPacket
{
	uint16_t opcode;
	char* fileName;
	char* mode;
};

void buildErr(char *buf);
void parseReq(char *, reqPacket* packet);

void err()
{
	perror(PROGNAME);
	exit(1);
}

int main(int argc, char **argv)
{
	// check arguments
	if(argc < 2)
	{
		printf("Not enough arguments!\n");
		exit(0);
	}

	char buf[PACKET_SIZE];

	// socket
	int s, s2 = 0;
	if( (s = socket(AF_INET, SOCK_DGRAM, 0)) < 0)
		err();

	// bind
	struct sockaddr_in servaddr;
	bzero(&servaddr, sizeof(servaddr));
	servaddr.sin_family = AF_INET;
	servaddr.sin_addr.s_addr = htonl(INADDR_ANY);
	servaddr.sin_port = htons(atoi(argv[1]));

	if( bind(s, (struct sockaddr*) &servaddr, sizeof(servaddr)) < 0)
		err();

	while(1)
	{
		FILE* myFile;
		
		// read request
		struct sockaddr_in clientaddr;
		int clientaddrSize = sizeof(clientaddr);
		if(recvfrom(s, buf, sizeof(buf), 0, (struct sockaddr *)&clientaddr, &clientaddrSize) < 0)
			err();

		// parse request
		reqPacket req;
		parseReq(buf, &req);

		// get client IP info
		char* clientIP = inet_ntoa(clientaddr.sin_addr);

		// print request and IP
		char* op = (req.opcode == RRQ) ? "RRQ" : "WRQ";
		printf("%s %s %s from %s:%s\n", op, req.fileName, req.mode, clientIP, argv[1]);

		// make second random port socket for data transfer
		if((s2 = socket(AF_INET, SOCK_DGRAM, 0)) < 0) 
			err();

		// file not found
		if((myFile = fopen(req.fileName, "r")) == NULL) // file not found, send error and finish
		{
			// construct error message
			bzero(&buf, sizeof(buf));
			buildErr(buf);

			// write error message
			if(sendto(s2, buf, sizeof(buf), 0, (struct sockaddr*)&clientaddr, clientaddrSize) < 0)
				err();
		}

		// file found
		else
		{
		
			uint16_t blockNum = 1;
			int numBytes, prev, opcode, ackNum = 0;
			bzero(&buf, sizeof(buf));
			
			// for every packet in the file
			while( (numBytes = fread(buf+4, 1, 512, myFile)) > 0)
			{
				printf("%d %d\n", blockNum, numBytes);
				
				// build the header
				buf[0] = DATA >> 8;
				buf[1] = DATA;
				buf[2] = blockNum >> 8;
				buf[3] = blockNum;
				
				// send the packet
				if(sendto(s2, buf, numBytes+4, 0, (struct sockaddr*)&clientaddr, clientaddrSize) < 0)
					err();
				
				// get response ack
				if(recvfrom(s2, buf, sizeof(buf), 0, (struct sockaddr *)&clientaddr, &clientaddrSize) < 0)
					err();
				
				// check response ack
				opcode = ((int)buf[0] << 8) | buf[1];
				ackNum = ((int)buf[2] << 8) | buf[3];
				
				if( (opcode != ACK) || (ackNum != blockNum) )
				{
					blockNum--;
					fseek(myFile, 0-numBytes, SEEK_CUR);
				}
				
				// prep for next packet
				bzero(&buf, sizeof(buf));
				blockNum++;
				prev = numBytes;
			}
			
			// empty packet sent for special case
			if(prev == 512)
			{
				printf("%d %d\n", blockNum, numBytes);
				bzero(&buf, sizeof(buf));
				buf[0] = DATA >> 8;
				buf[1] = DATA;
				buf[2] = blockNum >> 8;
				buf[3] = blockNum;
				if(sendto(s2, buf, 4, 0, (struct sockaddr*)&clientaddr, clientaddrSize) < 0)
						err();
			}
		}
		
		close(s2);
	}

	// close connection and exit
	close(s);
	return 0;
}

void buildErr(char *buf)
{
	buf[0] = ERROR >> 8;
	buf[1] = ERROR;
	buf[2] = FILENOTFOUND >> 8;
	buf[3] = FILENOTFOUND;
	strcpy(buf+4, "File not found.");
	return;
}

void parseReq(char* buf, reqPacket* packet)
{
	packet->opcode = ((uint16_t)buf[0] << 8) |( uint16_t)buf[1];
	packet->fileName = buf + 2;
	packet->mode = buf + 2 + strlen(packet->fileName) + 1;
	return;
}