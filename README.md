Name: Chenxi Zhang
Student ID: 20671033
Quest ID: c462zhan

Tested on Student environment in 2 different machines with Python

1) Check the IP address
   Example: curl ifconfig.me

2) Start the nEmulator-linux386 first
   Example: ./nEmulator-linux386 10001 129.97.167.34 10004 10003 129.97.167.34 10002 1 0 1

3) Start the receiver with nEmulator's IP address, port number, and filename
   Example: ./receiver.sh 129.97.167.34 10003 10004 result.txt
   
4) Start the sender with nEmulator's IP address, port number, and filename
   Example: ./sender.sh 129.97.167.34 10001 10002 tiny.txt