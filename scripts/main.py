#! /user/bin/env python3

import cv2
import numpy as np
import os
import sys
import glob
import colorExtraction
import mouseEvent

def main():
	print("input your image dir : ", end='')
	input_files_dir = input()
	files = sorted(glob.glob(input_files_dir + "/*.jpg"))
	ip = colorExtraction.ColorExtraction()
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

		mouseData = mouseEvent.MouseEvent(window_name)

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
			elif k == ord('s'):
				save_mode = True
				load_mode = False
			elif k == ord('l'):
				load_mode = True
				save_mode = False
			elif ord('0') <= k <= ord('9') and (save_mode or load_mode):  # 数字キーが押された場合
				key_num = chr(k)
				if save_mode:
					ip.save_color(key_num)
					save_mode = False
				elif load_mode:
					ip.load_color(key_num)
					# トラックバーの位置を更新
					cv2.setTrackbarPos("Hue_min", window_name, ip.color_param["h_min"])
					cv2.setTrackbarPos("Hue_max", window_name, ip.color_param["h_max"])
					cv2.setTrackbarPos("Saturation_min", window_name, ip.color_param["s_min"])
					cv2.setTrackbarPos("Saturation_max", window_name, ip.color_param["s_max"])
					cv2.setTrackbarPos("Value_min", window_name, ip.color_param["v_min"])
					cv2.setTrackbarPos("Value_max", window_name, ip.color_param["v_max"])
					load_mode = False
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
