#! /user/bin/env python3
import os
import cv2
import numpy as np

class MagicWand:
	def __init__(self):
		self.color_ranges = []

	def preparation(self, image_data):
		# 画像を読み込む
		self.img = image_data
		# セグメンテーション結果を保存する変数を初期化
		self.segmented = np.zeros_like(self.img)

	def extract_similar_color(self, seed_point, radius=5, threshold=30):
		# 半径5の円型のマスクを作成
		mask_circle = np.zeros(self.img.shape[:2], dtype=np.uint8)
		cv2.circle(mask_circle, seed_point, radius, 1, thickness=-1)
		
		# クリックされた位置の色を取得
		seed_color = self.img[seed_point[1], seed_point[0]]

		# 色の範囲を設定
		color_range = [np.array([seed_color[0] - threshold, seed_color[1] - threshold, seed_color[2] - threshold]), 
					  np.array([seed_color[0] + threshold, seed_color[1] + threshold, seed_color[2] + threshold])]

		# 色範囲の履歴を追加
		self.color_ranges.append(color_range)

		# 類似色のマスクを作成
		mask_color = cv2.inRange(self.img, *color_range)

		# 両方のマスクを結合
		mask_combined = cv2.bitwise_or(mask_circle, mask_color)

		return mask_combined

	def remove_color(self, seed_point, radius=5, threshold=30):
		# 半径5の円型のマスクを作成
		mask_circle = np.zeros(self.img.shape[:2], dtype=np.uint8)
		cv2.circle(mask_circle, seed_point, radius, 1, thickness=-1)
		
		# クリックされた位置の色を取得
		seed_color = self.img[seed_point[1], seed_point[0]]

		# 色の範囲を設定
		color_range = [np.array([seed_color[0] - threshold, seed_color[1] - threshold, seed_color[2] - threshold]), 
					  np.array([seed_color[0] + threshold, seed_color[1] + threshold, seed_color[2] + threshold])]

		# 類似色のマスクを作成
		mask_color = cv2.inRange(self.img, *color_range)

		# 両方のマスクを結合
		mask_combined = cv2.bitwise_or(mask_circle, mask_color)

		# マスクを反転
		mask_inverted = cv2.bitwise_not(mask_combined)

		remove_region = cv2.bitwise_and(self.img, self.img, mask=mask_inverted)
		self.segmented = cv2.bitwise_and(self.segmented, remove_region)

	def apply_color_ranges(self):
		# 履歴に保存されたすべての色範囲を適用する
		for color_range in self.color_ranges:
			mask = cv2.inRange(self.img, *color_range)
			extracted_region = cv2.bitwise_and(self.img, self.img, mask=mask)
			self.segmented = cv2.bitwise_or(self.segmented, extracted_region)

	def undo_last_change(self):
		if self.color_ranges:
			self.segmented = np.zeros_like(self.img)
			self.color_ranges.pop()  # 最後の変更を削除
			self.apply_color_ranges()  # 残りの履歴を再適用

	def run(self, x, y):
		mask = self.extract_similar_color((x, y))
		extracted_region = cv2.bitwise_and(self.img, self.img, mask=mask)
		self.segmented = cv2.bitwise_or(self.segmented, extracted_region)

