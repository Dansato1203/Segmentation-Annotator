#! /user/bin/env python3

import cv2
from PIL import Image, ImageDraw
import numpy as np
import glob

class ColorBase_Annotator:
	def __init__(self):
		self.color_mode = "none"
		self.color_param = {"h_min": 0, "h_max": 180, "s_min": 0, "s_max": 255, "v_min": 0, "v_max": 255}
		self.colors = {"none": self.color_param}
		self.saved_colors = {}

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

