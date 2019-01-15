#!/usr/bin/env python
import rospy
import message_filters as mf
import socket
from multijoy.msg import MultiJoy
from sensor_msgs.msg import Joy
from time import sleep
import sys
import struct

def putSock(oData):
    try:
        host = socket.gethostname()  # get local machine name
        port = 8888  # Make sure it's within the > 1024 $$ <65535 range
        #print("gonna send")
        s = socket.socket()
        s.connect((host, port))
        s.send(oData)
        #print('Sent: ' + oData)
        s.close()
    except:
        pass

def packDEEZNUTZ(message, joyNum): #object to bytes
    return struct.pack(\
    'iiffffffiiiiiiiiiiii',\
    message.header.stamp.secs,\
    message.header.stamp.nsecs,\
    message.joys[joyNum].axes[0],\
    message.joys[joyNum].axes[1],\
    message.joys[joyNum].axes[2],\
    message.joys[joyNum].axes[3],\
    message.joys[joyNum].axes[4],\
    message.joys[joyNum].axes[5],\
    message.joys[joyNum].buttons[0],\
    message.joys[joyNum].buttons[1],\
    message.joys[joyNum].buttons[2],\
    message.joys[joyNum].buttons[3],\
    message.joys[joyNum].buttons[4],\
    message.joys[joyNum].buttons[5],\
    message.joys[joyNum].buttons[6],\
    message.joys[joyNum].buttons[7],\
    message.joys[joyNum].buttons[8],\
    message.joys[joyNum].buttons[9],\
    message.joys[joyNum].buttons[10],\
    message.joys[joyNum].buttons[11])

class MultiJoyParser(object):
    
    def __init__(self):

        # Retrieve parameters
        self.ns=rospy.get_name()
	self.param_name_debug=self.ns+'/debug'
        self.param_name_njoys=self.ns+'/njoys'
        if rospy.has_param(self.param_name_debug):
            self.debug=rospy.get_param(self.param_name_debug)
        else:
            self.debug=False
        self.njoys=rospy.get_param(self.param_name_njoys)

        if self.debug:
            rospy.loginfo('debug={}'.format(self.debug))
            rospy.loginfo('njoys={}'.format(self.njoys))
            
        # Setup ros publisher
        self.multijoy_pub=rospy.Publisher('/multijoy', MultiJoy, queue_size=1)

        # Setup ros subscribers
        self.joy_subs=[mf.Subscriber('/joy/'+str(i),Joy, queue_size=1) for i in xrange(self.njoys)]
        self.timeSync=mf.ApproximateTimeSynchronizer(self.joy_subs, 10, self.njoys*100)
        self.timeSync.registerCallback(self.update)



    def update(self, *args):
        msg=MultiJoy()
        msg.header.stamp=rospy.Time.now()
        msg.njoys.data=self.njoys
        msg.joys=args
        print(msg)
        putSock(packDEEZNUTZ(msg, 0))
        #self.multijoy_pub.publish(msg)
        if self.debug:
            rospy.loginfo('joys retrieved and published')

if __name__=='__main__':
    rospy.init_node('multijoy_node')
    parser=MultiJoyParser()
    rospy.spin()
