#!/usr/bin/env python
import sys
import rospy
import serial
import paramiko
import socket
from multijoy.msg import MultiJoy
from sensor_msgs.msg import Joy
from time import sleep

import struct
server = '192.168.1.201' #ip of connected ubiquiti device
numJoys = int(1)
'''
#rf_uart = serial.Serial('/dev/serial/by-id/usb-Silicon_Labs_Base433_0001-if00-port0', 19200, timeout=.01)

def getRF(size_of_payload): #added argument to make it more function-like
    rf_uart.setDTR(True) #if the extra pins on the ttl usb are connected to m0 & m1 on the ebyte module
    rf_uart.setRTS(True) #then these two lines will send low logic to both which puts the module in transmit mode 0
    while True:
        n = rf_uart.read(1) #read bytes one at a time
        if not n:
            return 0
        if n == b's': #throw away bytes until start byte is encountered
            data = rf_uart.read(size_of_payload) #read fixed number of bytes
            n = rf_uart.read(1) #the following byte should be the stop byte
            if n == b'f':
                return data
            else: #if that last byte wasn't the stop byte then something is out of sync
                return -1
    return -1 #should never hit this return
'''

def getSock():
    try:
        host = socket.gethostname()   # get local machine name
        port = 8888  # Make sure it's within the > 1024 $$ <65535 range

        s = socket.socket()
        s.bind((host, port))
        print("Listening...")
        s.listen(1)
        client_socket, addr = s.accept()
        #print("Connection from: " + str(addr))
        while True:
            data = client_socket.recv(1024)
            #print(data)
            #print("Size: " + str(sys.getsizeof(data)))
            if data:
                break
            print('Data Received')
        s.close()
        return data
    except:
        pass

def get_RSSI():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server, username="admin", password="titanrover17")

    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("mca-status | grep signal")
    signal = ssh_stdout.readlines()[0]
    signal = int('-' + ''.join(i for i in signal if i.isdigit()))
    return signal

def unpackDEEZNUTZ(message): #object to bytes
    try:
        data = struct.unpack('iiffffffiiiiiiiiiiii', message)
        t_msg = MultiJoy()
        t_joy = Joy()
        t_joy.header.stamp.secs = data[0]
        t_joy.header.stamp.nsecs = data[1]

        for i in range(2, 8):
            t_joy.axes.append(data[i])
        print("axes")
        for i in range(6):
            print(t_joy.axes[i])
        for i in range(8, 20):
            t_joy.buttons.append(data[i])
        print("buttons")
        for i in range(0, 12):
            print(t_joy.buttons[i])
        return t_joy
    except:
        print(":LKJAFGHAFALKJFASFLKJ")


def monitor():
    multijoy_pub=rospy.Publisher('/multijoy', MultiJoy, queue_size=1)   #publisher for multijoy
    #Status_pub = rospy.Publisher('Status', Status, queue_size=1)

    rospy.init_node('MHz_Publisher', anonymous=True)
    #rospy.init_node('Rover_Status_Publisher', anonymous=True)
    rate = rospy.Rate(10) # 10hz
    while not rospy.is_shutdown():
        sleep(0.1)
        message = getSock()
        msg = MultiJoy()
        joy0 = Joy()
        print("TYPE")
        print(type(msg))
        if message:
            joy0 = unpackDEEZNUTZ(message)
            print(joy0)
            print("***")
            #msg.header = 'test'
            print(msg.header)
            print(joy0.header)
            msg.header = joy0.header
            print("header!!")
            print(msg.header)
            msg.njoys.data = 1
            print("njoys data!!")
            print msg.njoys.data
            msg.joys.append(joy0)
            print("joys!!")
            print(msg.joys)
            print("msg!!")
            print(msg)
            print("BB")
            multijoy_pub.publish(msg)
        '''
        RSSI = get_RSSI()
        if RSSI <= -70:
            data = getRF(42) #need to enter size of 2 Joy messages
            rospy.loginfo(data)
            multijoy_pub.publish(data)
            status_data = Status()
            status_data.source = 2
            Status_pub.publish(status_data)
            rate.sleep()
        '''

if __name__ == '__main__':
    try:
        monitor()
    except rospy.ROSInterruptException:
        pass