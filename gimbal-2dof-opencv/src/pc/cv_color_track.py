'''
多元高斯分布 色块识别
----------------------------
作者: 阿凯爱玩机器人
微信: xingshunkai
邮箱: xingshunkai@qq.com
更新日期: 2022/03/03
'''
import time
import glob
import pickle
import cv2
import numpy as np
from scipy.stats import multivariate_normal
from camera import Camera

class ColorBlockDetector:
	'''色块检测器'''
	# 颜色的名称
	color_names = ['red', 'green', 'blue', 'yellow'] 
	# 可视化-颜色的BGR值
	color_bgr = {
		'red': (0, 0, 255),
		'green': (0, 255, 0),
		'blue': (255, 0, 0),
		'yellow': (0, 255, 255)
	}

	bin_pdf_threshold = 0.0000001 # 图像二值化的概率密度阈值
	def __init__(self):
		# 每次载入之前都更新一次
		self.color_rgb_statis()
		# 载入图像信息
		self.load_color_info()
		
	def color_rgb_statis(self):
		'''BGR颜色空间下的颜色统计'''
		conv_bgr_dict = {}
		mean_bgr_dict = {}

		# 遍历所有的颜色
		for color_name in ['red', 'green', 'blue', 'yellow']:
			img_paths = glob.glob(f'./data/roi_image/{color_name}/*.png')
			bgr_list = []
			for img_path in img_paths:
				img = cv2.imread(img_path)
				bgr_list += list(img.reshape(-1, 3))
			bgr_list = np.uint8(bgr_list)
			# 协方差矩阵
			conv_bgr = np.cov(np.float32(bgr_list.T))
			# 均值
			mean_bgr = np.mean(np.float32(bgr_list.T), axis=1)
			# 添加到字典
			conv_bgr_dict[color_name] = conv_bgr
			mean_bgr_dict[color_name] = mean_bgr
		# 构建颜色信息
		self.color_info  = {}
		self.color_info['cov'] = conv_bgr_dict
		self.color_info['mean'] = mean_bgr_dict
		# 对象序列化并保存
		with open('config/color_block_statis.bin', 'wb') as f:
			pickle.dump(self.color_info, f)
	
	def load_color_info(self):
		'''载入颜色信息'''
		# 载入统计数据
		with open('config/color_block_statis.bin', 'rb') as f:
			self.color_info = pickle.load(f)
		# 创建统计信息 多元正态分布
		self.multi_normal = {}
		for color_name in self.color_names:
			mean = self.color_info['mean'][color_name] # 均值
			cov = self.color_info['cov'][color_name] # 协方差矩阵
			self.multi_normal[color_name] = multivariate_normal(mean=mean, cov=cov)
	
	def img_bgr2binary(self, img_bgr, color_name):
		'''BGR图像转换为灰度值'''
		img_h, img_w = img_bgr.shape[:2]
		# 图像变形
		bgr_list = img_bgr.reshape(-1, 3)
		# 获取每个像素值的概率密度
		img_pdf_1d = self.multi_normal[color_name].pdf(bgr_list)
		# 使用概率密度进行二值化
		binary = np.uint8((img_pdf_1d.reshape(img_h, img_w) >= self.bin_pdf_threshold)) * 255
		# 数学形态学操作
		binary = cv2.erode(binary, np.ones((3, 3)))
		binary = cv2.dilate(binary, np.ones((9, 9)))
		return binary
	def is_legal_rect(self, rect):
		'''判断矩形框是否合法'''
		x, y, w, h = rect
		# 过滤掉小噪点
		if w < 50 or h < 50:
			return False
		return True

	def color_clock_rect(self, img_bgr, color_name):
		'''获取色块的矩形区域'''
		# 创建画布
		canvas = np.copy(img_bgr)
		rect_list = []
		# 图像二值化
		bianry = self.img_bgr2binary(img_bgr, color_name)
		# 连通域检测
		*_, contours, hierarchy = cv2.findContours(image=bianry,mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_SIMPLE)
		# 计算外接矩形
		for cnt in contours:
			# 计算外界矩形
			rect = cv2.boundingRect(cnt)
			# 判断是否合法
			if self.is_legal_rect(rect):
				# 添加外接矩形到列表
				rect_list.append(rect)
				# 绘制矩形框
				x, y, w, h = rect
				color = self.color_bgr[color_name]
				cv2.rectangle(canvas, (x, y), (x+w, y+h), color, thickness=4)

		return rect_list, canvas

class ColorBlockTracker:
	'''色块跟踪'''
	def __init__(self, color_name="red"):
		'''初始化'''
		self.img_cnt = 0 # 帧计数
		# 创建检测器
		self.detector = ColorBlockDetector()
		# 创建跟踪器
		self.tracker = cv2.TrackerKCF_create()
		# 设置要追踪的颜色
		self.set_color(color_name)

	def set_color(self, color_name):
		'''设置颜色'''
		self.color_name = color_name
		self.tracker = cv2.TrackerKCF_create()
		self.last_roi = None # 上次检测到的目标色块的中心位置

	def select_target_rect(self, rects):
		'''选择目标矩形区域'''
		# 简单一点，条件设置为面积最大的矩形框
		if len(rects) == 0:
			return None
		# 返回面积最大的那个
		return max(rects, key=lambda rect: rect[2]*rect[3])
	
	@property
	def last_center(self):
		'''获取最新中心点'''
		if self.last_roi is None:
			return None
		x, y, w, h = self.last_roi
		return (x+w/2, y+h/2)

	def update(self, img):
		'''更新跟踪器的状态'''
		# 图像拷贝
		self.canvas = np.copy(img)
		self.img_cnt += 1
		
		if self.img_cnt + 1 >= 10:
			# 重置计数
			self.img_cnt = 0
			# 如果画面中存在ROI区域就在ROI区域进行检索
			if self.last_roi is not None:
				img_h, img_w = img.shape[:2]
				x, y, w, h = self.last_roi
				# 设置检索区域
				win_radius = 100 # 搜索半径
				sx = x - win_radius
				sx = 0 if sx < 0 else sx
				sy = y - win_radius
				sy = 0 if sy < 0 else sy
				sw = w + 2*win_radius
				sh = h + 2*win_radius
				sw = sw if sx+sw  <= img_w else img_w - sx
				sh = sh if sy+sh <= img_h else img_h - sy
				img_roi = img[sy:sy+sh, sx:sx+sw]
				roi_rect_list, _ = self.detector.color_clock_rect(img_roi, self.color_name)
				if len(roi_rect_list) > 0:
					# 更新ROI,添加偏移量
					(nx, ny, nw, nh) = self.select_target_rect(roi_rect_list)
					self.last_roi = (nx+sx, ny+sy, nw, nh)
					# 跟踪器初始化
					self.tracker = cv2.TrackerKCF_create()
					self.tracker.init(img, self.last_roi)
					# 在画面中绘制跟踪对象
					x, y, w, h = self.last_roi
					cv2.rectangle(self.canvas, (x, y), (x + w, y + h), (0, 255, 255), 4)
					return True
		
		if self.last_roi is None:
			# 上一帧没有检测到目标对象
			self.rect_list, self.canvas = self.detector.color_clock_rect(img, self.color_name)
			self.last_roi = self.select_target_rect(self.rect_list)
			if self.last_roi is None:
				# 图像识别还是没有识别到
				return False
			else:
				# 识别到了矩形区域, 初始化tracker
				# print("初始化跟踪器-1")
				self.tracker = cv2.TrackerKCF_create()
				self.tracker.init(img, self.last_roi)
		else:
			# 上一帧有参考
			is_success, box = self.tracker.update(img)
			# print("track is success: {}".format(is_success))
			if not is_success:
				# 跟踪失败，再次启动检测器
				# 上一帧没有检测到目标对象
				self.rect_list, self.canvas = self.detector.color_clock_rect(img, self.color_name)
				self.last_roi = self.select_target_rect(self.rect_list)
				if self.last_roi is None:
					# 图像识别还是没有识别到
					return False
				else:
					# 识别到了矩形区域, 初始化tracker
					# print("初始化跟踪器-2")
					self.tracker = cv2.TrackerKCF_create()
					self.tracker.init(img, self.last_roi)

			else:
				# 跟踪器检测成功, 提取roi区域
				self.last_roi = [int(v) for v in box]

		# 在画面中绘制跟踪对象
		x, y, w, h = self.last_roi
		cv2.rectangle(self.canvas, (x, y), (x + w, y + h), (0, 255, 255), 4)
		# 绘制颜色标签
		color = self.detector.color_bgr[self.color_name]
		cv2.putText(self.canvas, text=f"{self.color_name}",\
			org=(x, y), fontFace=cv2.FONT_HERSHEY_SIMPLEX, \
			fontScale=0.8, thickness=2, lineType=cv2.LINE_AA, color=color)
		return True

if __name__ == "__main__":
	# 要识别的颜色
	# 颜色可选范围 “red”, “green”, "blue", "yellow"
	TARGET_COLOR = "blue"
	# 创建摄像头
	camera = Camera()
	capture = camera.get_video_capture()
	# 色块跟踪
	color_block_tracker = ColorBlockTracker()
	# 设置跟踪的颜色
	color_block_tracker.set_color(TARGET_COLOR)

	while True:
		# 开始时间
		t_start = time.time()
		ret, img_bgr = camera.capture.read()
		if not ret:
			break
		# 跟踪器 更新
		color_block_tracker.update(img_bgr)
		# 选择要检测的颜色
		t_end = time.time()
		t_pass = t_end - t_start
		fps = int(1/t_pass)

		# 绘制帧率
		cv2.putText(color_block_tracker.canvas, text=f"FPS:{fps}",\
			org=(20, 20), fontFace=cv2.FONT_HERSHEY_SIMPLEX, \
			fontScale=0.8, thickness=2, lineType=cv2.LINE_AA, color=(0, 0, 255))
		
		cv2.imshow("canvas", color_block_tracker.canvas)
		key = cv2.waitKey(1)
		if key == ord('q'):
			break
	cv2.destroyAllWindows()
	camera.capture.release()