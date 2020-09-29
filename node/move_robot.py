#! /usr/bin/env python 
#ensures script is interpreted as python
import rospy
from geometry_msgs.msg import Twist

#tell rospy the name of the node, 'topic_publisher'
rospy.init_node('topic_publisher')
#declare that node is publishing to '/cmd_vel' topic using mssg type Twist
#queue_size argument limits amount of queued messages
pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)

#loop twice a second
rate = rospy.Rate(2)

move = Twist()
move.linear.x = 0.5
move.angular.z = 0.5

while not rospy.is_shutdown():
    pub.publish(move)
    rate.sleep()
