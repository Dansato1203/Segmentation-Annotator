#! /user/bin/env python3
import os
import cv2
import numpy as np

class MagicWand:
	def __init__(self, file_num, image_path):
		# 画像を読み込む
		self.image_path = image_path
		self.img = cv2.imread(self.image_path, cv2.IMREAD_COLOR)
		# セグメンテーション結果を保存する変数を初期化
		self.segmented = np.zeros_like(self.img)

		self.file_number = file_num

	def extract_similar_color(self, seed_point, radius=5, threshold=30):
		# 半径5の円型のマスクを作成
		mask_circle = np.zeros(self.img.shape[:2], dtype=np.uint8)
		cv2.circle(mask_circle, seed_point, radius, 1, thickness=-1)
		
		# クリックされた位置の色を取得
		seed_color = self.img[seed_point[1], seed_point[0]]

		# 色の範囲を設定
		lower = np.array([seed_color[0] - threshold, seed_color[1] - threshold, seed_color[2] - threshold])
		upper = np.array([seed_color[0] + threshold, seed_color[1] + threshold, seed_color[2] + threshold])

		# 類似色のマスクを作成
		mask_color = cv2.inRange(self.img, lower, upper)

		# 両方のマスクを結合
		mask_combined = cv2.bitwise_or(mask_circle, mask_color)

		return mask_combined

	def on_mouse_event(self, event, x, y, flags, param):
		if param["window_name"] == "Original Image" and event == cv2.EVENT_LBUTTONDOWN:
			mask = self.extract_similar_color((x, y))
			extracted_region = cv2.bitwise_and(self.img, self.img, mask=mask)
			self.segmented = cv2.bitwise_or(self.segmented, extracted_region)
			cv2.imshow("Segmented Image", self.segmented)
		elif param["window_name"] == "Segmented Image":
			if (event == cv2.EVENT_LBUTTONDOWN) or \
				(event == cv2.EVENT_MOUSEMOVE and (flags & cv2.EVENT_FLAG_LBUTTON)):
				# 半径3の円のマスクを作成
				mask_circle = np.zeros(self.segmented.shape[:2], dtype=np.uint8)
				cv2.circle(mask_circle, (x, y), 3, 255, thickness=-1)

				# マスクを反転して指定領域を黒くする
				mask_inv = cv2.bitwise_not(mask_circle)
				self.segmented = cv2.bitwise_and(self.segmented, self.segmented, mask=mask_inv)
				cv2.imshow("Segmented Image", self.segmented)

	#TODO : 他のモジュールと共通しているので統一する
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
		cv2.imwrite(annotate_img_name, self.segmented)

	def run(self):
		cv2.namedWindow("Original Image")
		cv2.namedWindow("Segmented Image")

		# マウスイベントのコールバックを設定
		cv2.setMouseCallback("Original Image", self.on_mouse_event, param={"window_name": "Original Image"})
		cv2.setMouseCallback("Segmented Image", self.on_mouse_event, param={"window_name": "Segmented Image"})

		# 画像を表示
		cv2.imshow("Original Image", self.img)
		cv2.imshow("Segmented Image", self.segmented)

		# ESCキーが押されるまで待機
		while True:
			key = cv2.waitKey(1) & 0xFF
			if key == ord('n'):
				self.file_number = self.file_number+1
				self.save_image(self.image_path)
				break
			elif key == ord('b'):
				self.file_number = self.file_number-1
				self.save_image(self.image_path)
				break
			if key == 27:
				break

		cv2.destroyAllWindows()
