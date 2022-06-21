#!/usr/bin/python
# -*- coding: UTF-8 -*-
from dronekit import connect, VehicleMode, LocationGlobal, LocationGlobalRelative
from pymavlink import mavutil # Needed for command message definitions
import time
import math
import cv2
import numpy as np
import threading
cam = cv2.VideoCapture(0)
def color_detection(frame):
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
                    if radius > 60:                  
                    	detect = color[0]
                    	#print(detect)
	return detect
def traffic():
    global color
    global red_count
    global blue_count
    global green_count
    global target_color
    global stop
    while True:
        print("color detection %s " % color)
        if color == "":
            red_count, blue_count, green_count = 0, 0, 0
        else:
            if color == "red" or color == "red2":
                color = "red"
                if color == "red":
                    red_count += 1
                    green_count, blue_count = 0, 0
                    print("red_count %s " % red_count)
                    if red_count >= 1:
                        print("stop")
			red_count, green_count, blue_count = 0, 0, 0
                        #vehicle.channels.overrides['2'] = 1500
                        red_count, blue_count, green_count, stop = 0, 0, 0, 1
            elif color == "green" and stop == 1:
                green_count+=1
                red_count, blue_count = 0, 0
                print("green_count %s " % green_count)
                if green_count == 3:
                    target_color = "green"
                    #vehicle.channels.overrides['2'] = 1410
                    print("go, target color %s " % target_color)
                    red_count, blue_count, green_count = 0, 0, 0
                    break
            elif color == "blue" and stop == 1:
                blue_count+=1
                red_count, green_count = 0, 0
                print("blue_count %s " % blue_count)
                if green_count == 3:
                    target_color = "green"
                    #vehicle.channels.overrides['2'] = 1410
                    print("go, target color %s " % target_color)
                    red_count, blue_count, green_count = 0, 0, 0
                    break
	time.sleep(0.1)
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

def img_process(img):
    #width x height 4:3
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3,3), 0)
    ret, thresh = cv2.threshold(blur, 60, 255, cv2.THRESH_BINARY_INV)
    return thresh
def line_contours(img):
    try:
        thresh = img_process(img)
        contours, hierarchy = cv2.findContours(thresh, 1, cv2.CHAIN_APPROX_NONE)
        if len(contours) > 0:
            c = max(contours, key=cv2.contourArea)
            M = cv2.moments(c) 
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            return cx ,cy
        else: 
            return 0, 0
    except:
        return 0, 0
def land():
    vehicle.channels.overrides['1']=1498
    time.sleep(0.1)
    vehicle.channels.overrides['2']=1499
    time.sleep(0.1)
    vehicle.channels.overrides['4']=1499
    time.sleep(0.1)
    print("c1 %s ch2 %s ch4 %s " % (vehicle.channels['1'], vehicle.channels['2'], vehicle.channels['4']))
    vehicle.mode = VehicleMode("LAND")
    print("current mode %s " % vehicle.mode.name)
    time.sleep(1)
def pid():
	global dx
	print("pid")
	if dx>100:
		print("left")
		#vehicle.channels.overrides['1'] = 1470		
	if dx<100 and dx > 60:
		print("on track")
		#vehicle.channels.overrides['1'] = 1498
	if dx<60:
		print("right")
		#vehicle.channels.overrides['1'] = 1520
	
def takeoff(TargetAlt):
    print("pre-arm checks")
    print("Arming motors")
    vehicle.mode = VehicleMode("LOITER")
    print("Current mode %s" %vehicle.mode.name)
    vehicle.armed = True
    print("TargetAlt %s " % TargetAlt)
    #vehicle.rangefinder.distance
    while True:
        current_mode = vehicle.mode.name
        print("motor %s " % vehicle.channels['3'])
	if current_mode != "LAND":
	    print("take off")
            current_alt = vehicle.rangefinder.distance
            print("current_alt %s " % current_alt)
            
            if current_alt >= TargetAlt*0.9:
                print("current_alt %s, Altitude hold %s " % (current_alt, vehicle.channels['3']))
                vehicle.channels.overrides['3'] = 1665
                vehicle.channels.overrides['3'] = 1665
                vehicle.channels.overrides['3'] = 1665
                print("motor %s " % vehicle.channels['3'])
                #forward()
                break
           
            elif current_alt >= TargetAlt*0.8:
                print("slow down")
                vehicle.channels.overrides['3'] = 1700
		#print("slow down %s" % vehicle.channels['3'])
            
            else:
                print("rise")
                vehicle.channels.overrides['3'] = 1760
	else:
		print("Current mode %s " % vehicle.mode.name)
		break
	time.sleep(0.1)
def forward():
	print("forward")
	vehicle.channels.overrides['2'] = 1410
	time.sleep(3)	
def draw_line(img, cx, cy):
    #text = " x,"+str(cx)+"y"+str(cy)
    cv2.line(img,(cx,0),(cx,720),(255,0,0),1)
    cv2.line(img,(0,cy),(1280,cy),(255,0,0),1)
    #cv2.putText(img, text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
    return img
width, height, half_height = 160, 120, 60
raspberry = "/dev/ttyS0"

device = raspberry
print("connect %s " %device)
#vehicle = connect(device, baud=57600, wait_ready=True)

#takeoff(1.25)
#time.sleep(1)

#forward()
dx=0

color = ""
red_count, green_count, blue_count, stop = 0, 0, 0, 0
c = threading.Thread(target=traffic)
c.daemon = True
c.start()
loop = True

while loop:
	#while vehicle.mode.name != "LAND":
	while True:
		ret, frame = cam.read()
		print("A")
	        res = cv2.resize(frame, (width, height), interpolation=cv2.INTER_NEAREST)
		color = color_detection(frame)        
	        #crop image
	        up_frame = res[0:half_height, 0:width]
	        down_frame = res[half_height:height, 0:width]
	        ux, uy = line_contours(up_frame)
		dx, dy = line_contours(down_frame)

		#pid()
	        no_line = ux+uy
		#cv2.imshow('up', up_frame)
	        #cv2.imshow('up', draw_line(up_frame, ux, uy))
		#cv2.imshow('down', draw_line(down_frame, dx, dy))
	        if cv2.waitKey(10) == 27: 
            		break   
	land()
	loop = False
cv2.destroyAllWindow()
