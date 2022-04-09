#!/usr/bin/env python

import sys
import socket
import time
import threading
from queue import Queue
import scapy.all as scapy

class Device:
    def __init__(self, ip, mac):
        self.ip     = ip
        self.mac    = mac
        self.ports  = []

    def addPort(self, port):
        self.ports.append(port)

socket.setdefaulttimeout(0.5)

g_portQueue     = Queue()
g_ip            = ""
g_device        = Device("","")
g_deviceList    = []
g_deviceLock    = threading.Lock()

def scanNetwork(ipRange):
    arpRequestFrame                 = scapy.ARP(pdst = ipRange)
    broadcastEtherFrame             = scapy.Ether(dst = "ff:ff:ff:ff:ff:ff")   
    broadcastEtherArpRequestFrame   = broadcastEtherFrame / arpRequestFrame
    answeredList                    = scapy.srp(broadcastEtherArpRequestFrame, timeout = 1, verbose = False)[0]
    neatList                        = []

    for i in range(0, len(answeredList)):
        ip      = answeredList[i][1].psrc
        mac     = answeredList[i][1].hwsrc

        neatList.append(Device(ip, mac))

    return neatList

def portThread():
    while True:
        port = g_portQueue.get()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            con = s.connect((g_device.ip, port))
            with g_deviceLock:
                g_device.ports.append(port)
            con.close()
            
        except:
            pass
        g_portQueue.task_done()


deviceList = scanNetwork(sys.argv[1])
# Sort the list on the last number in the ip address
deviceList.sort(key=lambda d: int(d.ip.split(".")[3]))

deviceQueue = Queue()

for device in deviceList:
    g_ip = device.ip
    g_device = device
    g_portQueue = Queue()
    # print(g_ip)
    #create threads
    for x in range(100):
        t = threading.Thread(target = portThread)
        t.daemon = True
        t.start()

    #fill the port queue
    for port in range(1, 500):
        g_portQueue.put(port)
        # deviceQueue.put(device)
    # print(g_device.ports)
    g_deviceList.append(g_device)
    g_portQueue.join()
    


print("IP\t\tMAC\t\t\tPorts")
for device in g_deviceList:
    portString = ""
    for port in device.ports:
        portString = portString + str(port) + " "
    print(device.ip + "\t" + device.mac + "\t" + portString)
