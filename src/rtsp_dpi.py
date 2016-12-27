import sys
import dpkt

import rtsp

def read_file(filename):
    fd = open(filename)
    pcap = dpkt.pcap.Reader(fd)

    packets = []
    for ts, buf in pcap:
        packets.append(dpkt.ethernet.Ethernet(buf))

    rtsp_packets = rtsp.get_RTSP_packets(packets)
    print len(rtsp_packets)
    for packet in rtsp_packets:
        print packet, "\n"


def usage():
    print("### RTSP Deep Packet Inspection ###\n")
    print("rtsp_spi.py [filename]")
    print("\tfilename : pcap file")

def main(args):
    if(len(args) != 1):
        usage()
        return

    read_file(args[0])

if __name__ == '__main__':
    main(sys.argv[1:])