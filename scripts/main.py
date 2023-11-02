#! /user/bin/env python3

import cv2
import numpy as np
import glob
import colorExtraction
import magicWand

def main():
	print("input your image dir : ", end='')
	input_files_dir = input()
	files = sorted(glob.glob(input_files_dir + "/*.jpg"))
	file_num = 0
	mode = True

	while True:
		img_path = files[file_num]
		print(img_path)

		if mode == 1:
			# ColorExtraction インスタンスを作成し、run メソッドを呼び出す
			ip = colorExtraction.ColorExtraction(mode, file_num)
			ip.run(img_path)
			file_num = ip.file_number
			mode = ip.mode
		elif mode == 0:
			# magicWand インスタンスを作成し、run メソッドを呼び出す
			mw = magicWand.MagicWand(mode, file_num, img_path)
			mw.run()
			file_num = mw.file_number
			mode = mw.mode

	print("-------- finish --------")
	cv2.destroyAllWindows()

if __name__ == "__main__":
	main()

