'''
File:         baseESC.py
Authors:      Chary Vielma / Shripal Rawal
Emails:       chary.vielma@csu.fullerton.edu / rawalshreepal000@gmail.com
Description: Mobility script reads in a text file with configuration for various controllers. User actions
             are interpreted by pygame and mapped to rover Actions for wheel and arm control. Communicating 
             these values is handled by a separate classes.

             To start program with a different configuration than rumblepad, list .txt file after script name:
             e.g. <python version> mobility.py dual.txt
'''

import roslib
import rospy
from std_msgs.msg import String
from test_mobility import joystick
import sys
import os
import socket
import struct
from time import sleep, time, clock
from threading import Thread
import multiprocessing
import pygame
import numpy as np
import subprocess
import serial

global armAttached
armAttached = False

'''
global system
global armAction
system = subprocess.check_output("uname -a", shell=True).strip().decode("utf-8")
if "raspberrypi" in system:
    system = "pi"
    import RPi.GPIO as GPIO                 # For Arm Movement

    armAction = { 0 : {'pwm' : 17, 'dir' : 27, 'enab' : 22},
                  1 : {'pwm' : 16, 'dir' : 20, 'enab' : 21},
                  2 : {'pwm' : 18, 'dir' : 23, 'enab' : 24},
                  3 : {'pwm' : 5,  'dir' : 6,  'enab' : 13}
                }

    GPIO.setmode(GPIO.BCM)

    for i in range(len(armAction)):
        GPIO.setup(armAction[i]['pwm'], GPIO.OUT)
        GPIO.setup(armAction[i]['dir'], GPIO.OUT)
        GPIO.setup(armAction[i]['enab'], GPIO.OUT)

elif "tegra-ubuntu" in system:
    system = "tx2"
    sys.path.insert(0, subprocess.check_output('locate TitanRover2019 | head -1', shell=True).strip().decode('utf-8') + '/gpio/')
    from tx2gpio import Tx2Gpio
   
    armAction = { 0 : {'pwm' : 396, 'dir' : 466, 'enab' : 397},
                  1 : {'pwm' : 429, 'dir' : 428, 'enab' : 427},
                  2 : {'pwm' : 398, 'dir' : 298, 'enab' : 389},
                  3 : {'pwm' : 481, 'dir' : 254, 'enab' : 430}
                }
    
    pinsUsed = [ 396, 466, 397,
                 429, 428, 427,
                 398, 298, 389,
                 392, 296, 481 ]

    tx2 = Tx2Gpio(pinsUsed)                        # Instantiating The Class Object

    for i in range(len(pinsUsed)):
        tx2.setup(pinsUsed[i], 'out')

else:
    system = "none"

'''

rf_uart = serial.Serial('/dev/serial/by-id/usb-Silicon_Labs_Rover433_0001-if00-port0', 9600, timeout=None)

# To import packages from different Directories
rootDir = subprocess.check_output('locate TitanRover2019 | head -1', shell=True).strip().decode('utf-8')
sys.path.insert(0, rootDir + '/build/resources/python-packages')
from pysaber import DriveEsc

# Instantiating The Class Object
wheels = DriveEsc(128, "mixed")
armMix = DriveEsc(129, "notMixed")

'''
def runPwmPi():
    global armAction
    while True:
        GPIO.output(armAction[0]['pwm'], 1)
        sleep(.00038)
        GPIO.output(armAction[0]['pwm'], 0)
        sleep(.00003)

def runPwmTx2():
    global armAction
    while True:
        tx2.output(armAction[0]['pwm'], 1)
        sleep(.00038)
        tx2.output(armAction[0]['pwm'], 0)
        sleep(.00003)

def checkArmDirection(val):
    if val == -1:
        return '0' 
    elif val == 1:
        return '1'

def moveJoints(data):
    global armAction, system

    if system == 'tx2':
        for i in range(1):#len(data)):
            if data[i] != 0:
                tx2.output(armAction[i]['enab'], 0)
                tx2.output(armAction[i]['dir'], int(checkArmDirection(data[i])))
            else:
                tx2.output(armAction[i]['enab'], 1)

    elif system == 'pi':
        for i in range(1):#len(data)):
            if data[i] != 0:
                GPIO.output(armAction[i]['enab'], 0)
                GPIO.output(armAction[i]['dir'], int(checkArmDirection(data[i])))
            else:
                GPIO.output(armAction[i]['enab'], 1)
'''

def getRF(size_of_payload): #added argument to make it more function-like
    rf_uart.setDTR(True) #if the extra pins on the ttl usb are connected to m0 & m1 on the ebyte module
    rf_uart.setRTS(True) #then these two lines will send low logic to both which puts the module in transmit mode 0
    while True:
        n = rf_uart.read(1) #read bytes one at a time
        if n == b's': #throw away bytes until start byte is encountered
            data = rf_uart.read(size_of_payload) #read fixed number of bytes
            n = rf_uart.read(1) #the following byte should be the stop byte
            if n == b'f':
                #print('success')
                data = struct.unpack('2b', data)
                
                msg.header.stamp = rospy.Time.now()
                msg.header.frame_id = 'Titan Rover'
                msg.mobility.TurningX = int(data[0])
                msg.mobility.ForwardY = int(data[1])
                msg.arm.J1 = int()
                msg.arm.J2 = int()
                msg.arm.J3 = int()
                msg.arm.J4 = int()
                msg.arm.J51 = int()
                msg.arm.J52 = int()
                msg.mode.mode = int()
                joy.publish(msg)

            else: #if that last byte wasn't the stop byte then something is out of sync
                print("failure")
                


def main(data):
    try:
        wheels.driveBoth(data.x, data.y)
        '''
        if armAttached:
            moveJoints([int(outVals[4]), int(outVals[5]), int(outVals[6]), int(outVals[7])])
            if outVals[-1] != '4':
                armMix.driveBoth(int(outVals[2]), int(outVals[3]))                        
            else:
                armMix.driveBoth(-(int(outVals[3])), int(outVals[3]))    
        '''        
    except:
        print("Mobility-main-drive error")



if __name__ == '__main__':

    # Only start the threads if the arm is attached
    try:
        '''
        if armAttached:
            if system == 'tx2':
                p1 = multiprocessing.Process(target=runPwmTx2)
                p1.start()
            elif system == 'pi':
                p1 = multiprocessing.Process(target=runPwmTx2)
                p1.start()
        '''

        # Start the main loop
        joy = rospy.Publisher('joystick', joystick, queue_size=10)
        rospy.init_node('talker_base_mobility', anonymous=True)
        msg = joystick()
        
        rospy.init_node('listener', anonymous=True)
        rospy.Subscriber("joystick", joystick, main)
        rospy.spin()

    except (KeyboardInterrupt, SystemExit):
        #p1.terminate()
        rospy.signal_shutdown()
        raise