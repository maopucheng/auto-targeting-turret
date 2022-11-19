'''
通过鼠标勾选图像的ROI区域,并保存
----------------------------
作者: 阿凯爱玩机器人
微信: xingshunkai
邮箱: xingshunkai@qq.com
更新日期: 2022/03/03
'''
import os
import platform
import sys
import logging
import numpy as np
import cv2
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2 import QtCore
from pathlib import Path

logging.basicConfig(level=logging.INFO)

class ROI:
	def __init__(self, x, y, w, h):
		self.x = x
		self.y = y
		self.w = w
		self.h = h
	def __str__(self):
		return 'ROI=[x={}, y={}, w={}, h={}]'.format(self.x, self.y, self.w, self.h)

class ROISignal(QObject):
	'''自定义信号'''
	roi_info = Signal(ROI) # ROI信息

class SelectROILabel(QLabel):
	'''选择ROI区域的窗口'''
	def __init__(self, parent=None):
		super(SelectROILabel, self).__init__(parent)
		self.offset_x = 0 # 偏移量
		self.offset_y = 0
		
		self.has_img = False # 是否载入图像
		self.has_roi = False # 是否选择好了ROI区域
		self.init_roi() # 初始化ROI区域
		self.cv_img = None # 图像
		self.cv_canvas = None # 画布

		# 设置对其方式为居中对齐
		self.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
		# 设置Label的最小尺寸, 不是设置的话就只能放大, 不能缩小
		self.setMinimumHeight(50)
		self.setMinimumWidth(50)
		# 信号
		self.roi_signal = ROISignal()

	def update_canvas(self, qsize=None):
		'''添加图像标签'''
		if self.cv_img is None:
			# 没有图像
			return
		canvas_rgb = cv2.cvtColor(self.cv_canvas, cv2.COLOR_BGR2RGB)
		# 转换为QImage
		bytes_per_line = 3 * self.img_w
		self.q_img = QImage(canvas_rgb.data, self.img_w, self.img_h, bytes_per_line, QImage.Format_RGB888)
		
		# 创建一个PixMap的组件
		pixmap = QPixmap(self.q_img)
		# 按照原比例进行缩放
		if qsize is None:
			fit_pixmap = pixmap.scaled(self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
		else:
			fit_pixmap = pixmap.scaled(qsize.width(), qsize.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
		
		self.setPixmap(fit_pixmap)

	def get_posi_on_pixmap(self, event):
		'''获取鼠标在Pixmap上的坐标(注意不是QLabel)'''
		pixmap_off_x = (self.width() - self.pixmap().width()) // 2
		pixmap_off_y = (self.height() - self.pixmap().height()) // 2
		x = event.x() - pixmap_off_x
		y = event.y() - pixmap_off_y
		x = min(self.pixmap().width(), max(0, x))
		y = min(self.pixmap().height(), max(0, y))
		return (x, y)

	def mousePressEvent(self, event):
		'''鼠标按下'''
		if not self.has_img:
			return
		self.select_roi_flag = True
		self.x1, self.y1 = self.get_posi_on_pixmap(event)
		logging.info("鼠标按下: X1 = {} Y1 = {}".format(self.x1, self.y1))
		# 清空画布
		self.cv_canvas = np.copy(self.cv_img)
		self.update_canvas()

	def mouseMoveEvent(self, event):
		'''鼠标运动'''
		if not self.has_img:
			return
		# 不断更新画面
		if not self.select_roi_flag:
			return
		self.x2, self.y2 = self.get_posi_on_pixmap(event)
		self.roi = self.get_roi()
		# 绘制ROI
		self.draw_roi()
		# 更新画布
		self.update_canvas()
		# 获取当前的ROI区域
		x,y,w,h = self.get_roi()
		# 发送ROI的信号
		self.roi_signal.roi_info.emit(ROI(x, y, w, h))

	def mouseReleaseEvent(self, event):
		'''鼠标释放'''
		if not self.has_img:
			return
		self.x2, self.y2 = self.get_posi_on_pixmap(event)
		logging.info("鼠标抬起: X2 = {} Y2 = {}".format(self.x2, self.y2))
		logging.info("ROI区域: {}".format(self.get_roi()))
		self.select_roi_flag = False
		
		self.has_roi = True
		self.roi = self.get_roi()
		x,y,w,h = self.roi
		if w== 0 or h==0:
			self.has_roi = False
		
		if self.has_roi:
			# 发送ROI的信号
			self.roi_signal.roi_info.emit(ROI(x, y, w, h))

	def draw_roi(self):
		'''绘制ROI区域'''
		self.cv_canvas = np.copy(self.cv_img)
		x, y, w, h = self.get_roi() # self.roi # self.get_roi()
		cv2.rectangle(self.cv_canvas, (x, y), (x+w, y+h), (255, 0, 0), thickness=4)
		cv2.circle(self.cv_canvas, (x, y), 10, (255, 0, 0), -1)
		cv2.circle(self.cv_canvas, (x+w, y+h), 10, (255, 0, 0), -1)
		cv2.circle(self.cv_canvas, (x, y+h), 10, (255, 0, 0), -1)
		cv2.circle(self.cv_canvas, (x+w, y), 10, (255, 0, 0), -1)

	def get_roi(self):
		# if not hasattr(self, 'select_roi_flag') or not self.select_roi_flag:
		# 	return None
		# if not self.has_roi:
		# 	return None
		scalar  = self.img_w / self.pixmap().width() # 要放大的倍数
		# 获取当前的ROI区域
		x = int(min(self.x1, self.x2) * scalar)
		y = int(min(self.y1, self.y2) * scalar)
		w = int(abs(self.x1-self.x2) * scalar)
		h = int(abs(self.y1-self.y2) * scalar)
		return (x, y, w, h)
	
	def load_new_image(self, cv_img):
		'''展示图像'''
		self.has_img = True
		# self.select_roi_flag = False # 是否正在选取ROI区域
		self.cv_img = cv_img # 更新画面
		self.cv_canvas = np.copy(cv_img)
		# 转换为qimg
		height, width, channel = cv_img.shape
		self.img_h = height
		self.img_w = width
		# logging.info("图像宽度: {} 图像高度: {}".format(self.img_w, self.img_h))
		# self.update_canvas()

	def init_roi(self):
		'''ROI参数初始化'''
		self.has_roi = False
		self.x1 = 0
		self.y1 = 0
		self.x2 = 0
		self.y2 = 0

	def resizeEvent(self, event):
		'''窗口缩放事件'''
		if not self.has_img:
			return
		# 缩放图像
		self.update_canvas(self.size())

	def update(self, frame):
		self.load_new_image(frame)
		if self.has_roi:
			# 绘制ROI区域
			self.draw_roi()
		self.update_canvas()