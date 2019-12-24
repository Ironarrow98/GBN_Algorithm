#!/bin/bash


# Bash Script for CS456/656 Assignment 2
# Initialize Receiver Port (Please make sure to initialize the Receiver Port first)
# Parameters:
#    $1: <host address of the network emulator>
#    $2: <UDP port number used by the link emulator to receive ACKs from the receiver>
#    $3: <UDP port number used by the receiver to receive data from the emulator>
#    $4: <name of the file into which the received data is written>


python3 -m receiver $1 $2 $3 "$4"
