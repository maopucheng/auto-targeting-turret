#!/usr/bin/env python
'''
从视频流中读取画面
----------------------------
作者: 阿凯爱玩机器人
微信: xingshunkai
邮箱: xingshunkai@qq.com
更新日期: 2022/03/03
'''
import sys
import os
import glob
import yaml
import numpy as np
import cv2

from camera import Camera
from camera_calibration import CameraCalibration

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from gui_slider_btn import SliderButton
from gui_select_roi import SelectROILabel

class CameraLoadThread(QThread):
	'''相机载入线程'''
	def __init__(self, parent=None):
		super(CameraLoadThread, self).__init__(parent)
		self.cam_id = 0
		self.camera = None

	def update_camera_id(self, cam_id):
		'''设置摄像头'''
		self.cam_id = cam_id


	def run(self):
		''''运行线程'''
		try:
			print("[CameraLoadThread] 开始加载相机")
			if self.camera is not None:
				self.camera.capture.release()
				
			self.camera = Camera(self.cam_id)
			# 初始相机
			self.camera.init_camera()
			# 载入相机标定数据
			self.camera.load_cam_calib_data()
			print("[CameraLoadThread] 相机加载完成")
		except Exception as e:
			print("[CameraLoadThread]")
			print(e)

class CameraConnectWidget(QWidget):
	'''摄像头连接组件'''
	CAM_ID_MAX = 4
	def __init__(self, parent=None):
		super(CameraConnectWidget, self).__init__(parent)
		self.camera = None
		self.init_widget()
		self.init_timer()
		self.init_thread()

	def init_widget(self):
		'''GUI组件初始化'''
		# 设备扫描
		cam_id_list = self.get_candi_device()
		
		# 连接按钮
		self.connect_btn = SliderButton()
		self.connect_btn.button_state_changed.connect(self.connect_btn_handler)
		
		# 设备下拉框
		self.device_combobox = QComboBox()
		self.device_combobox.addItems([str(cam_id) for cam_id in cam_id_list])

		# 布局
		self.main_layout = QGridLayout()
		self.main_layout.addWidget(QLabel("摄像头 "), 0, 0, 1, 1, Qt.AlignLeft)
		self.main_layout.addWidget(self.connect_btn, 0, 1, 1, 1, Qt.AlignRight)
		self.main_layout.addWidget(QLabel("设备号 "), 1, 0, 1, 1, Qt.AlignLeft)
		self.main_layout.addWidget(self.device_combobox, 1, 1, 1, 1, Qt.AlignRight)

		# 设置布局
		self.setLayout(self.main_layout)
		self.setAttribute(Qt.WA_StyledBackground)
		self.setMaximumWidth(200)

	def init_timer(self):
		self.camera_timer = QTimer()
	
	def init_thread(self):
		self.cam_load_thread = CameraLoadThread()
		self.cam_load_thread.finished.connect(self.cam_loaded_handler)

	def cam_loaded_handler(self):
		print("相机载入完成")
		self.camera = self.cam_load_thread.camera
		# 定时器开启
		self.camera_timer.start(int(1000/self.camera.config['fps']))
		self.cam_connect_messagebox.setText("相机载入成功")
		# 自动关闭消息盒
		QTimer.singleShot(500, self.cam_connect_messagebox.close)
	
	def get_candi_device(self):
		'''获取候选的摄像头'''
		cam_id_list = []
		for cam_id in range(self.CAM_ID_MAX):
			cap = cv2.VideoCapture(cam_id)
			if cap.isOpened():
				cam_id_list.append(cam_id)
			cap.release()
		return cam_id_list
	
	def update_candi_device(self):
		'''更新候选设备'''
		print("更新候选设备")

	@Slot(bool)
	def connect_btn_handler(self, enable):
		'''连接按键处理器'''
		cam_id = int(self.device_combobox.currentText())
		if enable:
			print("连接摄像头 cam_id = {}".format(cam_id))
			self.cam_load_thread.update_camera_id(cam_id)
			self.cam_load_thread.start()
			# 下拉框失能
			self.device_combobox.setEnabled(False)
			# 显示提示框
			self.cam_connect_messagebox = QMessageBox()
			self.cam_connect_messagebox.setText("相机加载中")
			self.cam_connect_messagebox.setIcon(QMessageBox.Information)
			self.cam_connect_messagebox.setStandardButtons(QMessageBox.Ok)
			self.cam_connect_messagebox.exec()
			
		else:
			print("断开摄像头连接")
			# 定时器断开
			self.camera_timer.stop()
			self.camera = None
			# 下拉框使能
			self.device_combobox.setEnabled(True)
			

class CameraCalibrationThread(QThread):
	'''相机标定线程'''
	def __init__(self, parent=None):
		super(CameraCalibrationThread, self).__init__(parent)
	
	def run(self):
		''''运行线程'''
		cc = CameraCalibration()
		cc.print_parameter()
		cc.dump_camera_info()

class CameraViewSignal(QObject):
	window_closed = Signal(str)

class CameraView(QWidget):

	def __init__(self, camera=None, parent=None):
		super(CameraView, self).__init__(parent)
		self.signal = CameraViewSignal()
		
		self.video_size = QSize(640, 480)
		self.is_cali_data_loaded = False # 是否载入了图像标定数据
		self.is_rm_img_distor = False # 是否移除图像畸变
		
		self.img_save_path = 'data/sample' # 图像保存路径
		self.img_cnt = 0 # 图像保存计数
		self.init_widget()
		if camera is not None:
			self.camera = camera
		else:
			self.setup_camera()
		self.setup_thread()
		# 载入标定信息
		with open('config/camera_calibration.yaml', 'r', encoding='utf-8') as f:
			self.camera_cali_config = yaml.load(f.read(), Loader=yaml.SafeLoader)
	def init_widget(self):
		"""Initialize widgets.
		"""
		self.setWindowTitle("相机图像预览与相机标定")
		# self.image_label = QLabel()
		self.image_label = SelectROILabel()
		self.image_label.setFixedSize(self.video_size)
		# 按钮工具栏
		
		self.screenshot_btn = QPushButton()
		self.screenshot_btn.setIcon(QIcon('icon/cam-img-save.png')) # 设置Icon
		self.screenshot_btn.setIconSize(QSize(int(500/3), int(106/3))) # 设置图标的尺寸
		self.screenshot_btn.clicked.connect(self.save_img)

		self.save_roi_btn = QPushButton()
		self.save_roi_btn.setIcon(QIcon('icon/cam-save-roi.png')) # 设置Icon
		self.save_roi_btn.setIconSize(QSize(int(500/3), int(106/3))) # 设置图标的尺寸
		self.save_roi_btn.clicked.connect(self.save_roi)
		
		self.cam_cali_btn = QPushButton()
		self.cam_cali_btn.setIcon(QIcon('icon/cam-cali.png')) # 设置Icon
		self.cam_cali_btn.setIconSize(QSize(int(500/3), int(106/3))) # 设置图标的尺寸
		self.cam_cali_btn.clicked.connect(self.run_cam_calib)


		self.select_save_path_btn = QPushButton() # 选择图像保存路径的按钮
		self.select_save_path_btn.setIcon(QIcon("icon/cam-select-save-path.png")) # 设置Icon
		self.select_save_path_btn.setIconSize(QSize(int(502/3), int(108/3))) # 设置图标的尺寸
		self.select_save_path_btn.clicked.connect(self.select_img_save_path)


		self.cam_cali_btn.setEnabled(False)
		# self.quit_btn = QPushButton("退出")
		# self.quit_btn.clicked.connect(self.close)
		self.rm_img_distor_checkbox = QCheckBox("移除图像畸变")
		self.rm_img_distor_checkbox.setObjectName("rm_img_distor_checkbox")
		self.rm_img_distor_checkbox.stateChanged.connect(self.update_is_rm_img_distor)
		# 信息表单
		# self.save_path_tag = QLabel("图像保存路径")
		self.save_path_label = QLineEdit(self.img_save_path)# QLabel(self.img_save_path) # 图像保存路径
		self.save_path_label.setObjectName("save_path_edit")
		self.save_path_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed) # 设置策略
		self.img_cnt_tag = QLabel()
		self.img_cnt_tag.setFixedSize(int(380/3), int(108/3))
		self.img_cnt_tag.setObjectName("img_cnt_tag")
		self.img_cnt_edit = QLineEdit('0')		
		self.img_cnt_edit.setObjectName("img_cnt_edit")
		# 布局
		self.main_layout = QGridLayout()
		# 添加画面
		self.main_layout.addWidget(self.image_label, 0, 0, 1, 4, Qt.AlignCenter)
		# 添加路径选择
		self.main_layout.addWidget(self.save_path_label, 1, 0, 1, 2, Qt.AlignRight|Qt.AlignVCenter)
		self.main_layout.addWidget(self.select_save_path_btn, 1, 2, 1, 1, Qt.AlignLeft|Qt.AlignVCenter)
		# 图像计数
		img_cnt_layout = QHBoxLayout()
		img_cnt_layout.addWidget(self.img_cnt_tag)
		img_cnt_layout.addWidget(self.img_cnt_edit)
		self.main_layout.addLayout(img_cnt_layout, 1, 3, 1, 1, Qt.AlignLeft|Qt.AlignVCenter)
		# 按钮组
		self.main_layout.addWidget(self.screenshot_btn, 2, 0, 1, 1, Qt.AlignCenter)
		self.main_layout.addWidget(self.save_roi_btn, 2, 1, 1, 1, Qt.AlignCenter)
		self.main_layout.addWidget(self.cam_cali_btn, 2, 2, 1, 1, Qt.AlignCenter)
		# 移除相机畸变
		self.main_layout.addWidget(self.rm_img_distor_checkbox, 2, 3, 1, 1, Qt.AlignLeft)
		self.main_layout.setSpacing(0)
		# 设置布局
		self.setLayout(self.main_layout)
		# 设置属性
		self.setAttribute(Qt.WA_StyledBackground)
		# 加载样式文件
		with open("./qss/camera_viewer.qss", "r", encoding="utf-8") as qs:
			self.setStyleSheet(qs.read())

	def setup_thread(self):
		self.cam_cali_thread = CameraCalibrationThread()
		self.cam_cali_thread.started.connect(self.before_cam_cali)
		self.cam_cali_thread.finished.connect(self.after_cam_cali)

	def setup_camera(self):
		"""Initialize camera.
		"""
		# 创建相机对象
		self.camera = Camera()
		# 初始相机
		self.camera.init_camera()
		self.capture = self.camera.get_video_capture()
		
		self.timer = QTimer()
		self.timer.timeout.connect(self.display_video_stream)
		self.timer.start(int(1000 / self.camera.config['fps']))

	def select_img_save_path(self):
		'''选择图像保存路径'''
		dialog = QFileDialog(self)
		dialog.setDirectory(os.getcwd())
		path_selected = dialog.getExistingDirectory()
		if path_selected is not None and len(path_selected) > 0:
			self.img_save_path = path_selected
			self.save_path_label.setText(self.img_save_path)
			self.img_cnt = 0
			self.img_cnt_edit.setText("{}".format(self.img_cnt))
	def display_video_stream(self, frame=None):
		"""Read frame from camera and repaint QLabel widget.
		"""
		if frame is None:
			_, frame = self.camera.capture.read()
		
		if self.is_rm_img_distor:
			# 去除图像畸变
			frame = self.camera.remove_distortion(frame)
		self.image = np.copy(frame) # 更新图像信息

		# 转换为QImage
		# frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
		# image = QImage(frame, frame.shape[1], frame.shape[0], 
		# 			   frame.strides[0], QImage.Format_RGB888)
		# self.image_label.setPixmap(QPixmap.fromImage(image))

		self.image_label.update(self.image)
		# 检查是否可以进行相机标定
		if not self.cam_cali_btn.isEnabled():
			if len(glob.glob("./data/caliboard/*.png")) > 20:
				self.cam_cali_btn.setEnabled(True)
		# 判断是否可以勾选移除畸变
		if not self.is_cali_data_loaded:
			if os.path.isfile(self.camera_cali_config['cali_info_save_path']):
				self.rm_img_distor_checkbox.setEnabled(True)

	def update_is_rm_img_distor(self):
		state = self.rm_img_distor_checkbox.checkState()
		self.is_rm_img_distor = state == Qt.Checked
		if self.is_rm_img_distor:
			self.camera.load_cam_calib_data()

	def save_img(self):
		'''保存图像'''
		# 从输入框获更新img_cnt
		self.img_cnt = int(self.img_cnt_edit.text())
		print(f"更新之后的数据: {self.img_cnt}")
		# 获取图像保存地址
		img_save_path = f"{self.img_save_path}/{self.img_cnt}.png"
		# 图像保存
		# cv2.imwrite(, self.image)
		cv2.imencode('.png', self.image)[1].tofile(img_save_path)

		print(f"图像保存成功 {img_save_path}")
		# 计数增加
		self.img_cnt += 1
		self.img_cnt_edit.setText(f"{self.img_cnt}")

	def save_roi(self):
		'''保存ROI图像'''
		if not self.image_label.has_roi:
			warn_box = QMessageBox()
			warn_box.warning(self, "ROI图像保存", "保存前请先确认已选中ROI矩形框", warn_box.Ok)
			return
		# 从输入框获更新img_cnt
		self.img_cnt = int(self.img_cnt_edit.text())
		# 获取ROI信息
		x, y, w, h = self.image_label.get_roi()
		# 获取图像保存地址
		img_save_path = f"{self.img_save_path}/{self.img_cnt}.png"
		# 图像保存
		# cv2.imwrite(img_save_path, self.image[y:y+h, x:x+w])
		cv2.imencode('.png', self.image[y:y+h, x:x+w])[1].tofile(img_save_path)

		print(f"图像保存成功 {img_save_path}")
		# 计数增加
		self.img_cnt += 1
		self.img_cnt_edit.setText(f"{self.img_cnt}")

	def run_cam_calib(self):
		'''开启相机标定'''
		self.cam_cali_thread.start()

	def before_cam_cali(self):
		"""相机标定前"""
		self.cali_msg_box = QMessageBox()
		self.cali_msg_box.information(self, "相机标定", "标定进行中,请耐心等待", self.cali_msg_box.Ok)

	def after_cam_cali(self):
		"""相机标定后"""
		# 重新载入标定数据
		self.camera.load_cam_calib_data()
		self.cali_msg_box.close()
		# 信息提示
		self.cali_msg_box.information(self, "相机标定", "标定已完成", self.cali_msg_box.Ok)
	
	def closeEvent(self, event):
		
		if hasattr(self, 'timer') and self.camera:
			self.timer.stop() # 定时器停止
			del(self.timer)
			# self.camera.capture.release() # 释放摄像头

		self.signal.window_closed.emit('camera_view')
		
if __name__ == "__main__":
	app = QApplication(sys.argv)
	win = CameraView()
	win.show()
	sys.exit(app.exec_())
