import cv2

import cv2

class MouseEvent:
	def __init__(self, input_img_name):
		self.mouseEvent = {"x": None, "y": None, "event": None, "flags": None}
		cv2.setMouseCallback(input_img_name, self.__CallBackFunc, None)

	def __CallBackFunc(self, eventType, x, y, flags, userdata):
		self.mouseEvent["x"] = x
		self.mouseEvent["y"] = y
		self.mouseEvent["event"] = eventType
		self.mouseEvent["flags"] = flags

	def getData(self):
		return self.mouseEvent

	def getEvent(self):
		return self.mouseEvent["event"]

	def getFlags(self):
		return self.mouseEvent["flags"]

	def getPos(self):
		return (self.mouseEvent["x"], self.mouseEvent["y"])
