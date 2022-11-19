'''
自定义滑动条
----------------------------
作者: 阿凯爱玩机器人
微信: xingshunkai
邮箱: xingshunkai@qq.com
更新日期: 2022/03/03
'''
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

class KSlider(QSlider):
	def __init__(self, parent=None):
		super(KSlider, self).__init__(parent=parent)
		self.setAttribute(Qt.WA_StyledBackground)
		# 加载样式文件
		with open("./qss/slider.qss", "r", encoding="utf-8") as qs:
			self.setStyleSheet(qs.read())
		
	# def mousePressEvent(self, event):
	# 	'''重载鼠标点击事件'''
	# 	value = self.value
	# 	super(KSlider, self).mousePressEvent(event)
	# 	self.setValue(value)