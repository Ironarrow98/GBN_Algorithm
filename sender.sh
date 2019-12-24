#!/bin/bash



# Bash Script for CS456/656 Assignment 2
# Initialize Sender Port (Please make sure to initialize the Receiver Port first)
# Parameters:
#    $1: <host address of the network emulator>
#    $2: <UDP port number used by the emulator to receive data from the sender>
#    $3: <UDP port number used by the sender to receive ACKs from the emulator>
#    $4: <name of the file to be transferred>



python3 -m sender $1 $2 $3 "$4"
