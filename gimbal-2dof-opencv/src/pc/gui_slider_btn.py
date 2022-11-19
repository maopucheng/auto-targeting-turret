'''
滑动条样式
----------------------------
作者: 阿凯爱玩机器人
微信: xingshunkai
邮箱: xingshunkai@qq.com
更新日期: 2022/03/03
'''
import sys

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class SliderButton(QWidget):
	'''滑动按键'''
	button_state_changed = Signal(bool)
	def __init__(self,parent=None):
		super(SliderButton, self).__init__(parent)
		self.checked = False
		# 按键关闭的背景颜色
		self.color_off_background = QColor(255, 255, 255)
		# 按键打开的背景颜色
		self.color_on_background = QColor(254, 222, 195)

		# self.color_slider_off = QColor(100, 100, 100)
		self.color_slider_off = QColor(100, 100, 100)
		self.color_slider_on = QColor(249, 145, 52)
		# 文字颜色
		self.color_text_off = QColor(143, 143, 143)
		self.color_text_on = QColor(77, 77, 77)
		# self.color_text_on = QColor(249, 145, 52)
		# 开启与关闭的文本
		self.text_off = "OFF"
		self.text_on = "ON"
		
		self.space = 2
		self.rectRadius = 5
		self.step = self.width() / 50
		self.startX = 0
		self.endX = 0
		# 定时器初始化
		self.timer = QTimer(self)  # 初始化一个定时器
		self.timer.timeout.connect(self.updateValue)  # 计时结束调用operate()方法
		# 设置全局字体
		font_id = QFontDatabase.addApplicationFont("./font/有爱魔兽圆体-R.ttf")
		font_name = QFontDatabase.applicationFontFamilies(font_id)[0]
		self.setFont(QFont(font_name, 10))
		# 设置尺寸约束
		# self.setMaximumWidth(60)
		# self.setMaximumHeight(30)
		# self.setMinimumHeight(30)
		self.setFixedSize(60, 30)
	def updateValue(self):
		if self.checked:
			if self.startX < self.endX:
				self.startX = self.startX + self.step
			else:
				self.startX = self.endX
				self.timer.stop()
		else:
			if self.startX  > self.endX:
				self.startX = self.startX - self.step
			else:
				self.startX = self.endX
				self.timer.stop()

		self.update()


	def mousePressEvent(self,event):
		self.checked = not self.checked
		#发射信号
		self.button_state_changed.emit(self.checked)
		# 每次移动的步长为宽度的5分之一
		self.step = self.width() / 5
		#状态切换改变后自动计算终点坐标
		if self.checked:
			self.endX = self.width() - self.height()
		else:
			self.endX = 0
		self.timer.start(20)

	def paintEvent(self, evt):
		'''绘制准备工作, 启用反锯齿'''
		painter = QPainter()
		painter.begin(self)
		painter.setRenderHint(QPainter.Antialiasing)
		#绘制背景
		self.drawBackground(evt, painter)
		#绘制滑块
		self.drawSlider(evt, painter)
		#绘制文字
		self.drawText(evt, painter)
		painter.end()
	
	def drawText(self, event, painter):
		painter.save()
		if self.checked:
			painter.setPen(self.color_text_on)
			painter.drawText(0, 0, self.width() / 2 + self.space * 2, self.height(), Qt.AlignCenter, self.text_on)
		else:
			painter.setPen(self.color_text_off)
			painter.drawText(self.width() / 2, 0,self.width() / 2 - self.space, self.height(), Qt.AlignCenter, self.text_off)
		painter.restore()

	def drawBackground(self, event, painter):
		painter.save()
		painter.setPen(Qt.NoPen)

		if self.checked:
			painter.setBrush(self.color_on_background)
		else:
			painter.setBrush(self.color_off_background)

		rect = QRect(0, 0, self.width(), self.height())
		#半径为高度的一半
		radius = rect.height() / 2
		#圆的宽度为高度
		circleWidth = rect.height()

		path = QPainterPath()
		path.moveTo(radius, rect.left())
		path.arcTo(QRectF(rect.left(), rect.top(), circleWidth, circleWidth), 90, 180)
		path.lineTo(rect.width() - radius, rect.height())
		path.arcTo(QRectF(rect.width() - rect.height(), rect.top(), circleWidth, circleWidth), 270, 180)
		path.lineTo(radius, rect.top())

		painter.drawPath(path)
		painter.restore()

	def drawSlider(self, event, painter):
		painter.save()

		if self.checked:
			painter.setBrush(self.color_slider_on)
		else:
			painter.setBrush(self.color_slider_off)

		rect = QRect(0, 0, self.width(), self.height())
		sliderWidth = rect.height() - self.space * 2
		sliderRect = QRect(self.startX + self.space, self.space, sliderWidth, sliderWidth)
		painter.drawEllipse(sliderRect)
		painter.restore()

class MainWindow(QMainWindow):
	def __init__(self,parent=None):
		super(MainWindow, self).__init__(parent)
		self.resize(400,200)
		self.switchBtn = SliderButton(self)
		self.switchBtn.setGeometry(10,10,60,30)
		self.switchBtn.button_state_changed.connect(self.getState)
		self.status = self.statusBar()
		self.status.showMessage("this is a example", 5000)
		self.setWindowTitle("PyQt")

	def getState(self,checked):
		print("checked=", checked)


if __name__ == "__main__":
	app = QApplication(sys.argv)
	form = MainWindow()
	#form = SliderButton()
	form.show()
	sys.exit(app.exec_())