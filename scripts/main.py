#! /user/bin/env python3

import cv2
import numpy as np
import os
import sys
import glob

import mouse_event
import image_process

def main():
	print("input your image dir : ",end='')
	input_files_dir = input()
	files = sorted(glob.glob(input_files_dir + "/*.jpg"))
	ip = image_process.ColorBase_Annotator(color="green")
	i = 0
	click_points = []
	draw = False
	window_name = "annotation window"

	while True:
		img = cv2.imread(files[i])
		print(files[i])
		hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
		color_mode = ip.return_hsv_param()
		extract_img = ip.color_extraction(img, hsv_img, **color_mode)
		cv2.imshow(window_name, extract_img)

		cv2.imshow("origin_img", img)
		cv2.imshow(window_name, extract_img)
		mode = cv2.getTrackbarPos("mode_change", window_name)

		mouseData = mouse_event.MouseEvent(window_name)

		cv2.createTrackbar("Hue_min", window_name, color_mode["h_min"], 180, ip.callback_func)
		cv2.createTrackbar("Hue_max", window_name, color_mode["h_max"], 180, ip.callback_func)
		cv2.createTrackbar("Saturation_min", window_name, color_mode["s_min"], 255, ip.callback_func)
		cv2.createTrackbar("Saturation_max", window_name, color_mode["s_max"], 255, ip.callback_func)
		cv2.createTrackbar("Value_min", window_name, color_mode["v_min"], 255, ip.callback_func)
		cv2.createTrackbar("Value_max", window_name, color_mode["v_max"], 255, ip.callback_func)
		cv2.createTrackbar("mode_change", window_name, 0, 1, ip.callback_func)

		while True:
			extract_img = ip.color_extraction(img, hsv_img, **color_mode)

			[cv2.circle(extract_img, point, 10, (0,0,0), thickness=-1) for point in click_points]
			cv2.imshow(window_name, extract_img)

			color_mode["h_min"] = cv2.getTrackbarPos("Hue_min", window_name)
			color_mode["h_max"] = cv2.getTrackbarPos("Hue_max", window_name)
			color_mode["s_min"] = cv2.getTrackbarPos("Saturation_min", window_name)
			color_mode["s_max"] = cv2.getTrackbarPos("Saturation_max", window_name)
			color_mode["v_min"] = cv2.getTrackbarPos("Value_min", window_name)
			color_mode["v_max"] = cv2.getTrackbarPos("Value_max", window_name)
			mode = cv2.getTrackbarPos("mode_change", window_name)

			if mouseData.getEvent() == cv2.EVENT_LBUTTONDOWN:
				draw = True
				click_points.append(mouseData.getPos())
			if mouseData.getEvent() == cv2.EVENT_LBUTTONUP:
				draw = False
			if mouseData.getEvent() == cv2.EVENT_MOUSEMOVE and draw:
				#print(mouseData.getPos())
				if draw:
					click_points.append(mouseData.getPos())
			if mouseData.getEvent() == cv2.EVENT_RBUTTONDOWN:
				extract_img = ip.reset_drawing(img, extract_img, mouseData.getPos()[0], mouseData.getPos()[1], 10)

			k = cv2.waitKey(1)
			if k == ord('n'):
				click_points = list()
				i = i+1
				break
			if k == ord('b'):
				click_points = list()
				i = i-1
				break
			if k == ord('z'):
				click_points.pop()
			if k == 27:
				sys.exit()

	print("-------- finish --------")
	cv2.destroyAllWindows()

if __name__ == "__main__":
	main()
