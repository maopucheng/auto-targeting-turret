'''
人脸年龄估计
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
from cv_face_detect import FaceDetector

class AgeEstimator:
	'''年龄估计器'''
	# 年龄段名称
	AGE_NAME_LIST = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
	AGE_PROTO_PATH = "./models/cnn_age_gender_models/age_deploy.prototxt"
	AGE_MODEL_PATH = "./models/cnn_age_gender_models/age_net.caffemodel"
	MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
	def __init__(self):
		# 加载网络
		self.net = cv2.dnn.readNet(self.AGE_PROTO_PATH, self.AGE_MODEL_PATH)

	def get_age_list(self, img, rect_list, canvas=None):
		'''获取年龄列表'''
		if canvas is None:
			canvas = np.copy(img)
		age_idx_list = []
		age_name_list = [] 
		for rect in rect_list:
			x, y, w, h = rect
			# 获取人脸的图像
			img_face = img[y : y+h, x : x+w]
			# 转换为blob
			blob = cv2.dnn.blobFromImage(img_face, 1.0, (227, 227), self.MODEL_MEAN_VALUES, swapRB=False)
			# 设置网络输入
			self.net.setInput(blob)
			# 得到网络返回预测结果
			age_preds = self.net.forward()
			# 得到age的编号与标签
			age_idx = age_preds[0].argmax()
			age_name = self.AGE_NAME_LIST[age_idx]
			age_idx_list.append(age_idx)
			age_name_list.append(age_name)
			# 绘制标签
			cv2.putText(canvas, age_name, (x, y - 10), \
	   			cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), \
			  	2, cv2.LINE_AA)
		return age_idx_list, age_name_list, canvas

if __name__ == "__main__":
	from camera import Camera
	
	camera = Camera()
	capture = camera.get_video_capture()
	# 色块跟踪
	detector = FaceDetector()
	age_estimator = AgeEstimator()
	while True:
		t_start = time.time()
		ret,img_bgr = capture.read()
		if not ret:
			break
		# 人脸检测
		rect_list, conf_list, canvas = detector.detect_face(img_bgr)
		# 年龄预估
		age_idx_list, age_name_list, canvas = age_estimator.get_age_list(img_bgr, rect_list, canvas=canvas)
		
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