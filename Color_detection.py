#!/usr/bin/python
# -*- coding: UTF-8 -*-
import collections
import numpy as np
import cv2
def set_color_range ():
	dict = {}
#Blue
	lower_blue = np.array([105, 43, 46])
	upper_blue = np.array([115, 255, 255])
	color_list = []
	color_list.append(lower_blue)
	color_list.append(upper_blue)
	dict['blue'] = color_list
#Red
	lower_red = np.array([156, 43, 46])
	upper_red = np.array([180, 255, 255])
	color_list = []
	color_list.append(lower_red)
	color_list.append(upper_red)
	dict['red'] = color_list
#Red2
	lower_red = np.array([0, 43, 46])
	upper_red = np.array([10, 255, 255])
	color_list = []
	color_list.append(lower_red)
	color_list.append(upper_red)
	dict['red2'] = color_list
#Green
	lower_green = np.array([70, 43, 46])
	upper_green = np.array([85, 255, 255])
	color_list = []
	color_list.append(lower_green)
	color_list.append(upper_green)
	dict['green'] = color_list

	return dict
def get_img(frame):
	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	detect = ""
	color_dict = set_color_range()
	for color in color_dict.items():	
		hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

		mask = cv2.inRange(hsv, color[1][0], color[1][1])
		mask = cv2.erode(mask, None, iterations=2)
		mask = cv2.dilate(mask, None, iterations=2)
                
		cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
                
                # initialize center
		center = None
                
		if len(cnts) > 0:
                    c = max(cnts, key=cv2.contourArea)
                    # a = max(cnts, key=cv2.boxPoints)
                    # 確定面積最大的輪廓
                    ((x, y), radius) = cv2.minEnclosingCircle(c)
                    # print(a)
                    # 計算輪廓的大小
                    M = cv2.moments(c)
                    # 計算質心
                    center = (int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"]))
                    if radius > 70:                  
                    	detect = color[0]
                    	print(detect)
	return detect
cam = cv2.VideoCapture(0)
while True:
	#print("1")
	while cam.isOpened():
		ret, frame = cam.read()
		color = get_img(frame)
		print("color detection %s" % color)
		if color == "":
			red_count, blue_count, green_count = 0, 0, 0
		else:
			if color == "red" or color == "red2":
				color = "red"
				if color == "red":
					red_count += 1
					print("red_count %s " % red_count)
					if red_count == 1:
						print("stop")
		if cv2.waitKey(10) == 27: 
            		break   
cv2.destroyAllWindow()
