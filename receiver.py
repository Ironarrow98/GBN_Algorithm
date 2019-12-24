import socket
from packet import packet
import sys
import time


# Main function
def main(args):

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
    file_port = int(args[3])
    file_name = args[4]
    
    # Open files
    file = open(file_name, 'w+')
    Arrive_log = open('arrival.log', 'w+')
    
    # Create receiving packet
    receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiver_socket.bind(('', file_port))
    
    # Define useful variables
    next_seqnum = 0
    counter = 0
    first = True
    
    # Start receving packets
    while True:
        try:
            data_pkt = receiver_socket.recv(1024)
        except:
            print('Error: paeket error')
            sys.exit(2)
        
        # Process received packet
        data_packet = packet.parse_udp_data(data_pkt)
        
        # Recevied packet is file data
        if data_packet.type == 1:

            # Record received packet sequence number
            Arrive_log.write('%d\n' % data_packet.seq_num)
            
            # Update expected sequence number and write data to file if the sequence is expected
            if data_packet.seq_num == next_seqnum:
                file.write(data_packet.data)
                next_seqnum += 1
                next_seqnum = next_seqnum % packet.SEQ_NUM_MODULO
                ACK_pkt = packet.create_ack(data_packet.seq_num)
                first = False
            # Otherwise, ignore and resend the last/duplicate ACK
            else:
                last_ACK_seqnum = next_seqnum - 1
                if (last_ACK_seqnum < 0):
                    last_ACK_seqnum = 31
                ACK_pkt = packet.create_ack(last_ACK_seqnum)
            
            # Stop sending any ACK if it is first time and sequence number is not expected 
            if not first:
                receiver_socket.sendto(ACK_pkt.get_udp_data(), (naddr, host_port))
                counter += 1
        
        # Recevied packet is EOT
        elif data_packet.type == 2:
            receiver_socket.sendto(packet.create_eot(next_seqnum - 1).get_udp_data(), (naddr, host_port))
            sys.exit(0)
    
    # Close files
    file.close()
    Arrive_log.close()


# Wrapper main function
if __name__ == "__main__":
    main(sys.argv)