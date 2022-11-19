'''
人脸跟踪
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
# 人脸检测
from cv_face_detect import FaceDetector
# 年龄估计
from cv_age_estimator import AgeEstimator

class FaceTracker:
	'''人脸跟踪器'''
	SELECTION_STRATEGY_MAX_AREA = 1 # 最大面积策略
	SELECTION_STRATEGY_AGE_MIN = 2  # 最小年龄策略
	RESAMPLE_IMG_COUNT = 300		# 重采样频率  多少fps重新采一次
	NEIGHBOR_ROI_MAX_DISTANCE = 200 # 像素距离阈值
	AGE_SAMPLE_MAX_NUM = 30	 		# 年龄采集个数
	ENABLE_TRACKER = True 			# 追踪器是否开启
	def __init__(self, selection_strategy=None):
		# 设置选择策略
		if selection_strategy is None:
			selection_strategy = self.SELECTION_STRATEGY_MAX_AREA
		self.selection_strategy = selection_strategy
		# 图像计数
		self.img_cnt = 0
		# 创建检测器
		self.detector = FaceDetector()
		# 创建年龄估计器
		if self.selection_strategy in [self.SELECTION_STRATEGY_AGE_MIN]:
			self.age_estimator = AgeEstimator()
		# 创建跟踪器
		if self.ENABLE_TRACKER:
			self.tracker = cv2.TrackerKCF_create()
			self.is_tracker_init = False
			self.track_roi_confidence = 1.0 # 跟踪框的置信度
		# 上次检测到人脸的中心位置
		self.last_roi = None 
		# 年龄标签
		self.age_idx = None
		# 年龄采集标签次数
		self.age_sample_num = 0
		# 年龄队列
		self.age_idx_buffer = []
		# 人脸检测置信度
		self.confidence_threshold = 0.5
	def rect2center(self, rect):
		'''ROI矩形框->中心'''
		x, y, w, h = rect
		return int(x+w/2), int(y+h/2)

	def rect_distance(self, rect1, rect2):
		'''计算矩形框之间的距离'''
		x1, y1 = self.rect2center(rect1)
		x2, y2 = self.rect2center(rect2)
		return math.sqrt((x1-x2)**2 + (y1-y2)**2)

	@property
	def last_center(self):
		if self.last_roi is None:
			return None
		return self.rect2center(self.last_roi)
	
	def is_old_roi_exist(self, rects, confidence_list):
		'''判断旧的ROI是否还在'''
		min_distance = 1000000.0
		neighbor_roi = None
		# 检查最近的ROI是否还在
		if self.last_roi is None or len(rects) == 0:
			return False, None
		x, y, w, h = self.last_roi
		last_cx = x + w / 2
		last_cy = y + h / 2
		# 如果存在则计算与之前ROI中心距离的最小值
		rect_num = len(rects)
		for i in range(rect_num):
			conf = confidence_list[i]
			# if conf < self.detector.CONFIDENCE_THRESHOLD:
			# 	continue
			rect = rects[i]
			x, y, w, h = rect
			cur_cx = x + w / 2
			cur_cy = y + h / 2
			cur_distance = math.sqrt((cur_cx - last_cx)**2 + (cur_cy - last_cy)**2)
			if cur_distance < min_distance:
				min_distance = cur_distance
				neighbor_roi = rect
		if neighbor_roi is not None and min_distance <= self.NEIGHBOR_ROI_MAX_DISTANCE:
			# print(f"neighbor_roi : {neighbor_roi} min_dis : {min_distance}")
			return True, neighbor_roi
		return False, None
	
	def select_target_rect(self, img, rects, confidence_list):
		'''选择目标矩形区域'''
		# 条件选择为置信度最高的
		if len(rects) == 0:
			return None
		# 判断原来跟踪的对象还在不在
		if self.last_roi is not None:
			is_valid, rect = self.is_old_roi_exist(rects, confidence_list)
			if is_valid:
				# 原来的对象还在，不需要重新选择
				return rect
		
		if self.selection_strategy == self.SELECTION_STRATEGY_AGE_MIN:
			age_idx_list, age_name_list, _ = self.age_estimator.get_age_list(img, rects)
			# 选择年龄最小
			candi_idx = np.argmin(np.array(age_idx_list))
			self.age_idx = age_idx_list[candi_idx] # 更新年龄ID
			self.age_idx_buffer = []
			self.age_sample_num = 0
			return rects[candi_idx]
		elif self.last_roi is None:
			# 选择置信度最高的
			return rects[np.argmax(confidence_list)]
		else:
			# 选择一次距离上次检测的RECT距离最近的
			return min(rects, key=lambda rect:self.rect_distance(rect, self.last_roi))

	def update(self, img):
		'''更新跟踪器的状态'''
		age_idx_list = None
		# 图像拷贝
		self.canvas = np.copy(img)
		# 图像计数自增
		self.img_cnt += 1
		is_success = False
		# 上一帧有参考 跟踪器更新
		if self.is_tracker_init:
			is_success, box = self.tracker.update(img)
			if is_success:
				# 跟踪器检测成功, 提取roi区域
				last_roi = [int(v) for v in box]
				x, y, w, h = last_roi
				# 判断跟踪器里面的ROI是不是人脸
				img_roi = img[y:y+h, x:x+w]
				rect_list, confidence_list, _ = self.detector.detect_face(img_roi, confidence_threshold=self.confidence_threshold)
				if len(confidence_list) == 0:
					self.track_roi_confidence -= 0.1
					if self.track_roi_confidence < 0:
						self.track_roi_confidence = 0
					self.confidence_threshold = 0.15
				else:
					self.track_roi_confidence = 1.0
					self.confidence_threshold = 0.5
				if self.track_roi_confidence <= 0:
					print("人脸跟踪丢失")
					is_success = False
					self.is_tracker_init = False
				else:
					# print(f"跟踪器:  self.last_roi :  {self.last_roi}")
					self.last_roi = last_roi
					if self.selection_strategy in [self.SELECTION_STRATEGY_AGE_MIN]:
						# 更新下年龄
						if self.age_sample_num <= self.AGE_SAMPLE_MAX_NUM:
							age_idx_list, age_name_list, _ = self.age_estimator.get_age_list(img, [self.last_roi])
							age_idx = age_idx_list[0]
							self.age_sample_num += 1
							self.age_idx_buffer.append(age_idx)
							self.age_idx = np.mean(np.float32(self.age_idx_buffer))
			else:
				# 视觉跟踪失败
				self.is_tracker_init = False
		if not is_success or  self.last_roi is None or  ((not self.ENABLE_TRACKER or self.img_cnt >= self.RESAMPLE_IMG_COUNT) and len(rect_list) > 0):
			# 检测画面中的人脸
			rect_list, confidence_list, self.canvas = self.detector.detect_face(img, confidence_threshold=self.confidence_threshold)
			if len(confidence_list) == 0:
				self.last_roi = None
				self.is_tracker_init = False
			elif len(confidence_list) > 0:
				# print("confidect_max:  {}".format(np.max(np.float32(confidence_list))))
				# 选择最佳ROI
				last_roi = self.select_target_rect(img, rect_list, confidence_list)
				if self.ENABLE_TRACKER and last_roi is not None:
					# 识别到了矩形区域, 初始化tracker
					self.tracker = cv2.TrackerKCF_create()
					self.tracker.init(img, last_roi)
					self.is_tracker_init = True
					self.track_roi_confidence = 1.0
					self.confidence_threshold = 0.5
				if last_roi is not None:
					self.last_roi = last_roi
			
		# 在画面中绘制跟踪对象
		if self.last_roi is not None:
			x, y, w, h = self.last_roi
			cv2.rectangle(self.canvas, (x, y), (x + w, y + h), (0, 255, 255), 4)
			# 绘制颜色标签
			if self.selection_strategy in [self.SELECTION_STRATEGY_AGE_MIN]:
				age_idx = round(self.age_idx)
				age_name = self.age_estimator.AGE_NAME_LIST[age_idx]
				cv2.putText(self.canvas, text=f"{age_name}",\
					org=(x, y), fontFace=cv2.FONT_HERSHEY_SIMPLEX, \
					fontScale=0.8, thickness=2, lineType=cv2.LINE_AA, color=(0, 0, 255))
			else:
				cv2.putText(self.canvas, text="face",\
					org=(x, y), fontFace=cv2.FONT_HERSHEY_SIMPLEX, \
					fontScale=0.8, thickness=2, lineType=cv2.LINE_AA, color=(0, 0, 255))

		return True
if __name__ == "__main__":
	from camera import Camera
	
	camera = Camera()
	capture = camera.get_video_capture()
	# 色块跟踪
	# detector = FaceDetector()
	tracker = FaceTracker(selection_strategy=FaceTracker.SELECTION_STRATEGY_MAX_AREA)
	# tracker = FaceTracker(selection_strategy=FaceTracker.SELECTION_STRATEGY_AGE_MIN)

	# 指定视频编解码方式为MJPG
	codec = cv2.VideoWriter_fourcc(*'MJPG')
	fps = 30.0 # 指定写入帧率为20
	frame_size = (150, 200) # 指定窗口大小
	# 创建 VideoWriter对象
	out = cv2.VideoWriter('data/face_video.avi', codec, fps, frame_size)

	while True:
		t_start = time.time()
		ret,img = capture.read()
		if not ret:
			break
		# rect_list,canvas = detector.detect_face(img)
		tracker.update(img)
		# 选择要检测的颜色
		# rect_list, canvas = color_block_detector.color_clock_rect(img, 'red')
		t_end = time.time()
		t_pass = t_end - t_start
		fps = int(1/t_pass)

		# 绘制帧率
		cv2.putText(tracker.canvas, text=f"FPS:{fps}",\
			org=(20, 20), fontFace=cv2.FONT_HERSHEY_SIMPLEX, \
			fontScale=0.8, thickness=2, lineType=cv2.LINE_AA, color=(0, 0, 255))
		
		cv2.imshow("canvas", tracker.canvas)
		# 录像
		if tracker.last_roi is not None:
			x, y, w, h = tracker.last_roi
			# print(f"w = {w} h = {h}")
			face_img = img[y:y+h, x:x+w]
			face_img = cv2.resize(face_img, frame_size)
			out.write(face_img)
		key = cv2.waitKey(1)
		if key == ord('q'):
			break
	cv2.destroyAllWindows()
	camera.capture.release()
	# 视频保存释放
	out.release()