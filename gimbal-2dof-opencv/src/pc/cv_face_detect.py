'''
人脸检测
----------------------------
作者: 阿凯爱玩机器人
微信: xingshunkai
邮箱: xingshunkai@qq.com
更新日期: 2022/03/03
'''

import time
import math
import cv2
import numpy as np


class FaceDetector:
	'''人脸检测器'''
	CONFIDENCE_THRESHOLD = 0.5 # 置信度阈值
	ROI_PADDING = 20 # ROI的边缘拓展像素
	FACE_SIZE_MIN = 50 # 尺寸阈值 最小
	FACE_SIZE_MAX = 400 # 尺寸阈值 最大
	def __init__(self):
		# 网络模型和预训练模型
		face_proto = "./models/face_detector/opencv_face_detector.pbtxt"
		face_model = "./models/face_detector/opencv_face_detector_uint8.pb"
		# 人脸检测的网络和模型
		self.net = cv2.dnn.readNet(face_model, face_proto)

	def is_legal_face(self, face):
		'''判断人脸是否合法'''
		confidence = face[4]
		return confidence >= self.CONFIDENCE_THRESHOLD

	def adjust_xyxy(self, x1, y1, x2, y2, img_w, img_h):
		# 取出box框住的脸部进行检测,返回的是脸部图片
		padding = self.ROI_PADDING
		y1 = max(0, y1 - padding)
		y2 = min(y2 + padding, img_h-1)
		x1 = max(0, x1 - padding)
		x2 = min(x2 + padding, img_w - 1)
		return x1, y1, x2, y2
        
	def detect_face(self, img, confidence_threshold=None):
		'''检测人脸'''
		if confidence_threshold is None:
			confidence_threshold = self.CONFIDENCE_THRESHOLD
		# 拷贝
		canvas = img.copy()
		img_h, img_w, _  = canvas.shape
		# 从Image里面创建blob
		blob = cv2.dnn.blobFromImage(canvas, 1.0, (300, 300), [104, 117, 123], True, False)
		# blobFromImage(image[, scalefactor[, size[, mean[, swapRB[, crop[, ddepth]]]]]]) -> retval  返回值 
		# swapRB是交换第一个和最后一个通道   返回按NCHW尺寸顺序排列的4 Mat值
		self.net.setInput(blob)
		# 网络进行前向传播，检测人脸
		detections = self.net.forward()
		rect_list = []
		confidence_list = []

		for i in range(detections.shape[2]):
			# 获取置信度
			confidence = detections[0, 0, i, 2]
			if confidence < confidence_threshold:
				continue
			# 将模型输出的数值 转化为像素坐标
			# 格式: [x1, y1, x2, y2]
			x1 = int(detections[0, 0, i, 3] * img_w)
			y1 = int(detections[0, 0, i, 4] * img_h)
			x2 = int(detections[0, 0, i, 5] * img_w)
			y2 = int(detections[0, 0, i, 6] * img_h)
			# 重新调整ROI
			x1, y1, x2, y2 = self.adjust_xyxy(x1, y1, x2, y2, img_w, img_h)
			w = int(x2 - x1)
			h = int(y2 - y1)
			if w < self.FACE_SIZE_MIN or h < self.FACE_SIZE_MIN or w > self.FACE_SIZE_MAX or h > self.FACE_SIZE_MAX:
				continue
			confidence_list.append(confidence)
			rect_list.append([x1, y1, w, h])  # bounding box 的坐标
			# 绘制矩形框
			cv2.rectangle(canvas, (x1, y1), (x2, y2), (0, 255, 0), int(round(img_h / 150)),
						8)  # rectangle(img, pt1, pt2, color[, thickness[, lineType[, shift]]]) -> img
		return rect_list, confidence_list, canvas


if __name__ == "__main__":
	from camera import Camera
	
	camera = Camera()
	capture = camera.get_video_capture()
	# 色块跟踪
	detector = FaceDetector()

	while True:
		t_start = time.time()
		ret,img_bgr = capture.read()
		if not ret:
			break
		rect_list, conf_list, canvas = detector.detect_face(img_bgr)
		
		t_end = time.time()
		t_pass = t_end - t_start
		fps = int(1/t_pass)

		# 绘制帧率
		cv2.putText(canvas, text=f"FPS:{fps}",\
			org=(20, 20), fontFace=cv2.FONT_HERSHEY_SIMPLEX, \
			fontScale=0.8, thickness=2, lineType=cv2.LINE_AA, color=(0, 0, 255))
		
		cv2.imshow("canvas", canvas)
		key = cv2.waitKey(1)
		if key == ord('q'):
			break
	cv2.destroyAllWindows()
	camera.capture.release()
 