#! /usr/bin/env python3

import os
import numpy as np
import cv2

def save_processed_image(image_path, segmented_image):
	# 保存先ディレクトリのパスを作成
	label_dir = os.path.join(os.path.dirname(image_path), 'labels')
	if not os.path.exists(label_dir):
		os.makedirs(label_dir)

	# 保存するファイル名を決定
	base_name = os.path.splitext(os.path.basename(image_path))[0]
	save_path = os.path.join(label_dir, f"{base_name}_label.png")

	# 画像を保存
	cv2.imwrite(save_path, segmented_image)

def remove_segment_at_point(segmented_image, point, radius=10):
	"""
	指定された点にあるセグメントを削除する。
	:param segmented_image: セグメント化された画像
	:param point: セグメントを削除する点 (x, y)
	:param radius: 削除する範囲の半径
	:return: 更新されたセグメント画像
	"""
	mask = np.zeros(segmented_image.shape[:2], dtype=np.uint8)
	cv2.circle(mask, point, radius, 255, thickness=-1)
	mask_inverted = cv2.bitwise_not(mask)
	remove = cv2.bitwise_and(segmented_image, segmented_image, mask=mask_inverted)

	return cv2.bitwise_and(segmented_image, remove)
