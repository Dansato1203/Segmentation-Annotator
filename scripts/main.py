#! /user/bin/env python3

import cv2
import numpy as np
import glob
import colorExtraction

def main():
	print("input your image dir : ", end='')
	input_files_dir = input()
	files = sorted(glob.glob(input_files_dir + "/*.jpg"))
	file_num = 0

	while True:
		img_path = files[file_num]
		print(img_path)

		# ColorExtraction インスタンスを作成し、run メソッドを呼び出す
		ip = colorExtraction.ColorExtraction(file_num)
		ip.run(img_path)
		file_num = ip.file_number
#		k = cv2.waitKey(1) & 0XFF
#		if k == ord('n'):
#			file_num = file_num+1 if file_num < len(files) - 1 else file_num
#		elif k == ord('b'):
#			file_num = file_num-1 if file_num > 0 else i
#		elif k == 27:  # ESC key
#			sys.exit()

	print("-------- finish --------")
	cv2.destroyAllWindows()

if __name__ == "__main__":
	main()

