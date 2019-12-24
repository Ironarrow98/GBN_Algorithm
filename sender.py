import socket
from packet import packet
import sys
import threading
import time


# Define useful constants
N = 10
max_packet_length = 500
last_ACKed_Seqnum = -1
last_ACKed_Changed = False
rest_ACK = False
seqnum_lock = threading.Lock();
rest_ACK_lock = threading.Lock();


# Function for getting current time in miliseconds
def getTime():
    t = round(time.time() * 1000)
    return int(t)


# Function for ack receiver thread
def ACK_receiver(portNumber):
    
    # Call global variable
    global last_ACKed_Seqnum
    global last_ACKed_Changed
    global rest_ACK
    
    # Create new UDP socket and bind to avaliable port
    receiver_Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  
    # Create ACK receiver port
    receiver_Socket.bind(('', portNumber))

    # Start waiting for ACK
    while True:
        rest_ACK_lock.acquire()
       
        # Check if main thread ended
        if rest_ACK:
            rest_ACK_lock.release()
            return
        rest_ACK_lock.release()
        try:
            ACK_status = receiver_Socket.recv(1024)
        except:
            # Error case, the connection is lost or the message is invalid
            sys.exit(3)
        ACK_packet = packet.parse_udp_data(ACK_status)
        
        # Start receving ACK
        if (ACK_packet.type == 0):
            
            # Record ACK sequence number
            with open('ack.log', 'a+') as file:
                file.write("%d\n" % ACK_packet.seq_num)
                file.close()
                
            # Update last received ACK sequence number
            seqnum_lock.acquire()
            ACK_diff = ACK_packet.seq_num - last_ACKed_Seqnum
            if ACK_diff > 0:
                last_ACKed_Seqnum = ACK_packet.seq_num
                last_ACKed_Changed = True
            elif (ACK_diff >= (-31)) and (ACK_diff <= (-23)):
                last_ACKed_Seqnum = ACK_packet.seq_num
                last_ACKed_Changed = True
            seqnum_lock.release()
      

# Function for sending packets
def packets_sender(pkts, addr, port, rport):
    
    # Define useful constants
    base_seqnum = 0
    base_i = 0
    cur_pkt_i = 0    
    start_time = 0
    end_time = 0
    first = True
    pause = False
    
    # Call for global variables
    global N
    global last_ACKed_Seqnum
    global last_ACKed_Changed
    global rest_ACK
    
    # Create sender socket
    sender_Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sender_Socket.bind(('', 0))
    
    # Create new thread for ACK_receiver
    receiver = threading.Thread(target = ACK_receiver, args = (rport,))
    receiver.daemon = True
    receiver.start()
    
    # Record the start time
    start_time = getTime()
    
    # Start sending packets
    while base_i < len(pkts):
        
        # Check if new ack is received, update timer and new base sequence number
        seqnum_lock.acquire()
        if last_ACKed_Changed:
            last_ACKed_Changed = False
            newBase = last_ACKed_Seqnum + 1
            diff = newBase - base_seqnum
            if diff < 0:
                diff += 32
            if newBase > 31:
                newBase -= 32
            base_i += diff
            base_seqnum = newBase
            packet_timer = getTime()
        seqnum_lock.release()
        
        # Start timer for first time packet
        if first:
            packet_timer = getTime()
            first = False
        
        # See timer is expired or not
        t = getTime()
        if (t - packet_timer) > 100:
            cur_pkt_i = base_i
            packet_timer = getTime()
            pause = False
            
        # Send packets to the port
        if not pause:
            sender_Socket.sendto(pkts[cur_pkt_i].get_udp_data(), (addr, port))
            
            # Record sent packet
            with open('seqnum.log', 'a+') as file:
                file.write("%d\n" % pkts[cur_pkt_i].seq_num)
                file.close()
            
        # Check if reached packet window limit or not
        cur_pkt_i += 1
        if cur_pkt_i < (base_i + N) and cur_pkt_i < len(pkts):
            pause = False
        else:
            pause = True
            
    # Inform ACK_receiver thread to exit and send EOT
    rest_ACK_lock.acquire()
    rest_ACK = True
    rest_ACK_lock.release()
    EOT_pkt = packet.create_eot(len(pkts) - 1)
    sender_Socket.sendto(EOT_pkt.get_udp_data(), (addr, port))
    receiver.join()
    
    # Record the end time
    end_time = getTime()
    
    # Calculate and record the transmission time
    transmission_time = end_time - start_time
    time_log = open('time.log', 'w+')
    time_log.write("%d\n" % transmission_time)
    time_log.close()
    return


# Main function
def main(args):
    
    # Call global constant
    global max_packet_length
    
    # Check the number of arguments is correct or not
    if not len(args) == 5:
        print('Error 2: expected 5 arguments, %d was received' %(len(args)))
        sys.exit(2)
    
    # Check if the type of argument is correct
    if (not ((args[2]).isdigit())) or (not ((args[3]).isdigit())):
        print('Error 4: port number must be an integer')
        sys.exit(4)
    
    # Get arguments
    naddr = args[1]
    host_port = int(args[2])
    ACK_port = int(args[3])
    file_name = args[4]
    
    # Open and prepare files
    sfile = open(file_name, 'r')
    seqnum_log = open('seqnum.log', 'w+')
    ACK_log = open('ack.log', 'w+')
        
    # Make sure the log file is empty
    seqnum_log.write('')
    ACK_log.write('')
    seqnum_log.close()
    ACK_log.close()
        
    # Read send file content
    if sfile.mode == 'r':
        fileContent = sfile.read()
    else:
        print('Error: file permission denied')
        sys.exit(3)
    
    # Calculate the number of packets needed
    num_pkts = (len(fileContent)) // max_packet_length
    if len(fileContent) % max_packet_length > 0:
        num_pkts += 1
    
    # Create the packet window
    pkts = []
        
    # Save the packet to the list
    for i in range(0, num_pkts):
        if i == (num_pkts - 1):
            start = i * max_packet_length
            end = len(fileContent)
        else:
            offset = i * max_packet_length
            start = 0 + offset
            end = max_packet_length + offset
        newPkg = packet.create_packet(i, fileContent[start:end])
        pkts.append(newPkg)
        
    # Send the packets
    packets_sender(pkts, naddr, host_port, ACK_port)
    sys.exit(0)


# Wrapper main function
if __name__ == "__main__":
    main(sys.argv)