#! /usr/bin/env python3

import numpy as np
import cv2

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
