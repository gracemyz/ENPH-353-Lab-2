#!/usr/bin/env python
from __future__ import print_function

import roslib
#roslib.load_manifest('my_package')
import sys
import rospy
import cv2
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
from geometry_msgs.msg import Twist

lastError = 1
lineOnLeft = 0
lineOnRight = 0
x = 0.5
z = 0.5

class line_follower:



	def __init__(self):
		# publish to "image_topic_2" topic using message type Image
		self.image_pub = rospy.Publisher("image_topic_2",Image, queue_size = 1)

		self.bridge = CvBridge()
		# subscribe to raw image using message type Image; do callback when there is an image
		self.image_sub = rospy.Subscriber("/rrbot/camera1/image_raw",Image,self.callback)

		self.move_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)


	

	def callback(self,data):
		global lastError
		global lineOnRight
		global lineOnLeft
		global x
		global z
		try:
			# convert ROS image message into grayscale image
			# mono8 for grayscale, passthrough for no change
		  cv_image = self.bridge.imgmsg_to_cv2(data, 'mono8')
		except CvBridgeError as e:
		  print(e)    

		(rows,cols) = cv_image.shape
		centx = int(cols/2)
		centy = rows - 50
		cv2.circle(cv_image, (int(cols/2), rows - 50), 10, 255)
		#print(cv_image[50,50])
		# show encoded image in image window
		cv2.imshow("Image window", cv_image)
		cv2.waitKey(3)
		#loop twice a second
		#rate = rospy.Rate(2)
		colour_arr=[]

		i=0
		while (i < 16):
			colour_arr.append(cv_image[750, i * 50 ])
			i+=1



		num = 0
		denom = 0
		for i in range (len(colour_arr)):
			num += i * 100 * colour_arr[i]
			denom += colour_arr[i]

		position = num / denom
		print(position)
		print(colour_arr)


		error = position - 750
		kP = 0.1
		kD = 0.06
		speedAdjustment = kP * error + kD * (error - lastError)
		lastError = error
		baseSpeed = 1.5

		onWhite = 1

		# if the line is lost:
		for i in colour_arr:
			if  i < 100:
				onWhite = 0
				break

		if onWhite == 1:
			if lineOnLeft == 1:
				x = 0
				z = 2
				print("searching, left")
			elif lineOnRight == 1:
				x = 0
				z = -2
				print("searching, right")
		else:
			x = baseSpeed
			z = baseSpeed + speedAdjustment
			lav = int((colour_arr[0] + colour_arr[1] + colour_arr[2] + colour_arr[3] + colour_arr[4])/5)
			rav = int((colour_arr[15] + colour_arr[14] + colour_arr[13] + colour_arr[12] + colour_arr[11])/5)
			if rav < 110:
				print ("rav")
				print(rav)

				lineOnRight = 1
				lineOnLeft = 0
			elif lav < 110:
				print("lav")
				print(lav)
				lineOnLeft = 1
				lineOnRight = 0
			else:
				lineOnRight = 0
				lineOnLeft = 0



		if (z > 8):
			z = 8
		if (z < -8):
			z = -8

		move = Twist()
		move.linear.x = x
		move.angular.z = z
		print(z)
		#print(height, width)



		try:
		  self.image_pub.publish(self.bridge.cv2_to_imgmsg(cv_image, "passthrough"))
		  self.move_pub.publish(move)

		except CvBridgeError as e:
		  print(e)
		  #need exception for move_pub?

def main(args):
  rospy.init_node('line_follower', anonymous=True)

  lf = line_follower()



  try:
	rospy.spin()
  except KeyboardInterrupt:
	print("Shutting down")
  cv2.destroyAllWindows()

if __name__ == '__main__':
	main(sys.argv)