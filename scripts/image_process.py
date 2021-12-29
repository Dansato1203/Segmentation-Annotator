#! /user/bin/env python3

import cv2
from PIL import Image, ImageDraw
import numpy as np
import glob

class ColorBase_Annotator:
	def __init__(self, color):
		self.color_mode = color

		self.none_hsv = {"h_min": 0, "h_max": 180, "s_min": 0, "s_max": 255, "v_min": 0, "v_max": 255}
		self.green_hsv = {"h_min": 44, "h_max": 91, "s_min": 98, "s_max": 255, "v_min": 0, "v_max": 255}
		self.white_hsv = {"h_min": 0, "h_max": 180, "s_min": 0, "s_max": 45, "v_min": 100, "v_max": 255}

	def callback_func(self, val):
		pass

	def return_hsv_param(self):
		if self.color_mode == "none":
			return self.none_hsv
		elif self.color_mode == "green":
			return self.green_hsv
		elif self.color_mode == "white":
			return self.white_hsv

	def image_thresholding(self, img):
		pil_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
		pil_img = Image.fromarray(pil_img)
		pil_img = pil_img.convert('P')
		self.thresh_img = Image.new('P', (pil_img.size))
		for x in range(pil_img.size[0]):
			for y in range(pil_img.size[1]):
				pix = pil_img.getpixel((x, y))
				if pix != 0:
					# モード分ける時にここを条件分岐
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

	def color_extraction(self, img, hsv_img, h_min, h_max, s_min, s_max, v_min, v_max):
		hsv_min = np.array([h_min, s_min, v_min])
		hsv_max = np.array([h_max, s_max, v_max])

		img_mask = cv2.inRange(hsv_img, hsv_min, hsv_max)

		self.extraction_img = cv2.bitwise_and(img, img, mask=img_mask)
		return self.extraction_img
