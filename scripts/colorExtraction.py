#! /user/bin/env python3

import os
import cv2
from PIL import Image, ImageDraw
import numpy as np
import glob

class ColorExtraction:
	def __init__(self, mode, file_num):
		self.color_mode = "none"
		self.color_param = {"h_min": 0, "h_max": 180, "s_min": 0, "s_max": 255, "v_min": 0, "v_max": 255}
		self.colors = {"none": self.color_param}
		self.saved_colors = {}
		self.window_name = "annotation window"
		self.draw = False
		self.click_points = []
		self.circle_rad = []
		self.rad = 10
		self.mode = mode
		self.file_number = file_num


	def callback_func(self, val):
		pass

	def add_color(self, name, h_min, h_max, s_min, s_max, v_min, v_max):
		self.colors[name] = {"h_min": h_min, "h_max": h_max, "s_min": s_min, "s_max": s_max, "v_min": v_min, "v_max": v_max}

	def set_color_mode(self, mode):
		if mode in self.colors:
			self.color_mode = mode

	def get_hsv_param(self):
		return self.colors.get(self.color_mode, self.color_param)

	def image_thresholding(self, img):
		pil_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
		pil_img = Image.fromarray(pil_img)
		pil_img = pil_img.convert('P')
		self.thresh_img = Image.new('P', pil_img.size)
		for x in range(pil_img.size[0]):
			for y in range(pil_img.size[1]):
				pix = pil_img.getpixel((x, y))
				if pix != 0:
					self.thresh_img.putpixel((x, y), 50)
		self.thresh_img.putpalette(pil_img.getpalette())
		return self.thresh_img

	def reset_drawing(self, origin_img, annotation_img, x, y, margin):
		origin_img = Image.fromarray(origin_img)
		mask_img = Image.new("L", origin_img.size, 0)
		draw = ImageDraw.Draw(mask_img)
		draw.ellipse((x-5, y-5, x+5, y+5), fill=255)
		reset_img = Image.fromarray(annotation_img).copy()
		reset_img.paste(origin_img, (x, y), mask=mask_img)
		reset_cvimg = np.array(reset_img)
		return reset_cvimg

	def color_extraction(self, img, hsv_img):
		hsv_param = self.get_hsv_param()
		hsv_min = np.array([hsv_param["h_min"], hsv_param["s_min"], hsv_param["v_min"]])
		hsv_max = np.array([hsv_param["h_max"], hsv_param["s_max"], hsv_param["v_max"]])
		img_mask = cv2.inRange(hsv_img, hsv_min, hsv_max)
		self.extraction_img = cv2.bitwise_and(img, img, mask=img_mask)
		return self.extraction_img

	def save_color(self, key):
		self.saved_colors[key] = self.color_param.copy()
		print(f"Color parameters saved to key {key}")

	def load_color(self, key):
		if key in self.saved_colors:
			self.color_param = self.saved_colors[key]
			print(f"Loaded color parameters from key {key}")
		else:
			print(f"No color parameters saved for key {key}")

	def save_image(self, img_path):
		# パスを分割
		directory_path , file_name = os.path.split(img_path)
		img_name, _ = os.path.splitext(file_name)

		# ラベル用のディレクトリを作成
		label_directory = os.path.join(directory_path, 'labels')
		if not os.path.exists(label_directory):
			os.mkdir(label_directory)

		annotate_img_name = os.path.join(label_directory, (img_name + '_label.png'))
		print(annotate_img_name)
		cv2.imwrite(annotate_img_name, self.extraction_img)

	def __mouse_callback(self, event, x, y, flags, param):
		if event == cv2.EVENT_LBUTTONDOWN:
			self.draw = True
			self.click_points.append((x, y))
			self.circle_rad.append(self.rad)
		elif event == cv2.EVENT_LBUTTONUP:
			self.draw = False
		elif event == cv2.EVENT_MOUSEMOVE and self.draw:
			self.click_points.append((x, y))
			self.circle_rad.append(self.rad)
		elif event == cv2.EVENT_RBUTTONDOWN:
			self.reset_drawing(self.img, self.extract_img, x, y, 10)

	# TODO : magicWand.pyのコンストラクタと実装を統一する
	def run(self, img_path):
		self.img = cv2.imread(img_path)
		self.hsv_img = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)
		cv2.namedWindow(self.window_name)
		cv2.setMouseCallback(self.window_name, self.__mouse_callback)

		# トラックバーの設定
		color_mode = self.get_hsv_param()
		cv2.createTrackbar("Hue_min", self.window_name, color_mode["h_min"], 180, self.callback_func)
		cv2.createTrackbar("Hue_max", self.window_name, color_mode["h_max"], 180, self.callback_func)
		cv2.createTrackbar("Saturation_min", self.window_name, color_mode["s_min"], 255, self.callback_func)
		cv2.createTrackbar("Saturation_max", self.window_name, color_mode["s_max"], 255, self.callback_func)
		cv2.createTrackbar("Value_min", self.window_name, color_mode["v_min"], 255, self.callback_func)
		cv2.createTrackbar("Value_max", self.window_name, color_mode["v_max"], 255, self.callback_func)
		cv2.createTrackbar("Radius of circle", self.window_name, self.rad, 100, self.callback_func)

		save_mode = False
		load_mode = False

		while True:
			self.extract_img = self.color_extraction(self.img, self.hsv_img)
			for index, point in enumerate(self.click_points):
				draw_rad = self.circle_rad[index]
				cv2.circle(self.extract_img, point, draw_rad, (0,0,0), thickness=-1)
			cv2.imshow("origin_image", self.img)
			cv2.imshow(self.window_name, self.extract_img)

			color_mode["h_min"] = cv2.getTrackbarPos("Hue_min", self.window_name)
			color_mode["h_max"] = cv2.getTrackbarPos("Hue_max", self.window_name)
			color_mode["s_min"] = cv2.getTrackbarPos("Saturation_min", self.window_name)
			color_mode["s_max"] = cv2.getTrackbarPos("Saturation_max", self.window_name)
			color_mode["v_min"] = cv2.getTrackbarPos("Value_min", self.window_name)
			color_mode["v_max"] = cv2.getTrackbarPos("Value_max", self.window_name)
			self.rad = cv2.getTrackbarPos("Radius of circle", self.window_name)

			key = cv2.waitKey(1) & 0xFF
			if key == ord('n'):
				self.file_number = self.file_number+1
				self.save_image(img_path)
				break
			elif key == ord('b'):
				self.file_number = self.file_number-1
				self.save_image(img_path)
				break
			elif key == ord('s'):
				save_mode = True
				load_mode = False
			elif key == ord('l'):
				load_mode = True
				save_mode = False
			elif ord('0') <= key <= ord('9') and (save_mode or load_mode):  # 数字キーが押された場合
				key_num = chr(key)
				if save_mode:
					self.save_color(key_num)
					save_mode = False
				elif load_mode:
					self.load_color(key_num)
					# トラックバーの位置を更新
					cv2.setTrackbarPos("Hue_min", self.window_name, self.color_param["h_min"])
					cv2.setTrackbarPos("Hue_max", self.window_name, self.color_param["h_max"])
					cv2.setTrackbarPos("Saturation_min", self.window_name, self.color_param["s_min"])
					cv2.setTrackbarPos("Saturation_max", self.window_name, self.color_param["s_max"])
					cv2.setTrackbarPos("Value_min", self.window_name, self.color_param["v_min"])
					cv2.setTrackbarPos("Value_max", self.window_name, self.color_param["v_max"])
					load_mode = False
			elif key == ord('m'):
				self.mode = False
				break
			elif key == 27:  # ESC key
				break

		cv2.destroyAllWindows()

