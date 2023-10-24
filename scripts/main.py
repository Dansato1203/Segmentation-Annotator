#! /user/bin/env python3

import cv2
import numpy as np
import os
import sys
import glob
import image_process
import mouse_event

def main():
	print("input your image dir : ", end='')
	input_files_dir = input()
	files = sorted(glob.glob(input_files_dir + "/*.jpg"))
	ip = image_process.ColorBase_Annotator()
	i = 0
	rad = 10
	circle_rad = []
	click_points = []
	draw = False
	window_name = "annotation window"

	save_mode = False
	load_mode = False

	while True:
		img = cv2.imread(files[i])
		print(files[i])
		hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
		color_mode = ip.get_hsv_param()
		extract_img = ip.color_extraction(img, hsv_img)
		cv2.imshow(window_name, extract_img)
		cv2.imshow("origin_img", img)

		mouseData = mouse_event.MouseEvent(window_name)

		# トラックバーの設定
		cv2.createTrackbar("Hue_min", window_name, color_mode["h_min"], 180, ip.callback_func)
		cv2.createTrackbar("Hue_max", window_name, color_mode["h_max"], 180, ip.callback_func)
		cv2.createTrackbar("Saturation_min", window_name, color_mode["s_min"], 255, ip.callback_func)
		cv2.createTrackbar("Saturation_max", window_name, color_mode["s_max"], 255, ip.callback_func)
		cv2.createTrackbar("Value_min", window_name, color_mode["v_min"], 255, ip.callback_func)
		cv2.createTrackbar("Value_max", window_name, color_mode["v_max"], 255, ip.callback_func)
		cv2.createTrackbar("Radius of circle", window_name, rad, 100, ip.callback_func)

		while True:
			extract_img = ip.color_extraction(img, hsv_img)
			for index, point in enumerate(click_points):
				draw_rad = circle_rad[index]
				cv2.circle(extract_img, point, draw_rad, (0,0,0), thickness=-1)
			cv2.imshow(window_name, extract_img)

			color_mode["h_min"] = cv2.getTrackbarPos("Hue_min", window_name)
			color_mode["h_max"] = cv2.getTrackbarPos("Hue_max", window_name)
			color_mode["s_min"] = cv2.getTrackbarPos("Saturation_min", window_name)
			color_mode["s_max"] = cv2.getTrackbarPos("Saturation_max", window_name)
			color_mode["v_min"] = cv2.getTrackbarPos("Value_min", window_name)
			color_mode["v_max"] = cv2.getTrackbarPos("Value_max", window_name)
			rad = cv2.getTrackbarPos("Radius of circle", window_name)

			if mouseData.getEvent() == cv2.EVENT_LBUTTONDOWN:
				draw = True
				click_points.append(mouseData.getPos())
				circle_rad.append(rad)
			if mouseData.getEvent() == cv2.EVENT_LBUTTONUP:
				draw = False
			if mouseData.getEvent() == cv2.EVENT_MOUSEMOVE and draw:
				if draw:
					click_points.append(mouseData.getPos())
					circle_rad.append(rad)
			if mouseData.getEvent() == cv2.EVENT_RBUTTONDOWN:
				extract_img = ip.reset_drawing(img, extract_img, mouseData.getPos()[0], mouseData.getPos()[1], 10)

			k = cv2.waitKey(1)
			if k == ord('n'):
				click_points = list()
				circle_rad = list()
				i = i+1
				break
			elif k == ord('b'):
				click_points = list()
				circle_rad = list()
				i = i-1
				break
			elif k == ord('z'):
				click_points.pop()
				circle_rad.pop()
			elif k == 27:
				sys.exit()

		threshed_img = ip.image_thresholding(extract_img)
		fdir_name = os.path.split(files[i-1])
		file_name = os.path.splitext(fdir_name[-1])
		threshed_img.save(file_name[0] + "_label.png")

	print("-------- finish --------")
	cv2.destroyAllWindows()

if __name__ == "__main__":
	main()
