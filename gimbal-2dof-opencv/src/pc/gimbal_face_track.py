'''
云台人脸追踪
----------------------------
作者: 阿凯爱玩机器人
微信: xingshunkai
邮箱: xingshunkai@qq.com
更新日期: 2022/03/03
'''
import time
import numpy as np # 引入numpy 用于矩阵运算
import cv2
import yaml

from config import *
from PyFaceDet import facedetectcnn
from gimbal_uart_protocol import *
from cv_face_track import FaceTracker

  

# 配置是否录制人脸
IS_RECORD_FACE = True
# 获取相机ID
cam_config = None
with open('config/camera.yaml', 'r', encoding='utf-8') as f:
	cam_config = yaml.load(f.read(), Loader=yaml.SafeLoader)
# 摄像头ID
CAM_ID = cam_config["device"]

def update_gimbal_pid():
	global angle_down
	global angle_up
	global offset_x
	global offset_y
	global face_center
	px, py = face_center
	deadarea=0.15
 
 	# 比例系数
	k_down = 8
	k_up = 4
 	# 归一化 偏移量 [-1, 1]
	# offset_x +=  0.1*(2.0*(0.5 - px / IMG_WIDTH) - offset_x)
	offset_x = 2.0*(0.5 - px / IMG_WIDTH)
	offset_y = 2.0*(0.5 - py / IMG_HEIGHT)
	
	if abs(offset_x) > deadarea:
		# 更新底部舵机的PID
		angle_down += k_down * offset_x
		angle_down = max(ANGLE_MIN_DOWN, min(angle_down, ANGLE_MAX_DOWN))
	if abs(offset_y) > deadarea:
		# 更新上舵机的PID
		angle_up += k_up * offset_y
		angle_up = max(ANGLE_MIN_UP, min(angle_up, ANGLE_MAX_UP))
	# 设置舵机角度
	set_gimbal_raw_angle(angle_down, angle_up)


# 记录舵机云台位置
angle_down = ANGLE_DEFAULT_DOWN
angle_up = ANGLE_DEFAULT_UP
# 人脸中心
tracker = FaceTracker(selection_strategy=FaceTracker.SELECTION_STRATEGY_AGE_MIN)

face_center = (IMG_WIDTH/2, IMG_HEIGHT/2)
# 偏移量
offset_x = 0
offset_y = 0
# 舵机角度初始化
set_gimbal_raw_angle(angle_down, angle_up)
time.sleep(2)

# pid_timer = Timer(0.03, update_gimbal_pid)
# pid_timer.start()
# pid_timer.join()

# 创建一个video capture的实例
cap = cv2.VideoCapture(CAM_ID)
# 查看Video Capture是否已经打开
print("摄像头是否已经打开 ？ {}".format(cap.isOpened()))
## 设置画面的尺寸
# 画面宽度设定为 640
cap.set(cv2.CAP_PROP_FRAME_WIDTH, IMG_WIDTH)
# 画面高度度设定为 480
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, IMG_HEIGHT)
# 创建窗口
cv2.namedWindow('image_win',flags=cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)

if IS_RECORD_FACE:
    # 指定视频编解码方式为MJPG
	codec = cv2.VideoWriter_fourcc(*'MJPG')
	fps = 30.0 # 指定写入帧率为20
	frame_size = (150, 200) # 指定窗口大小
	# 创建 VideoWriter对象
	video_name = int(time.time())
	out = cv2.VideoWriter(f'data/{video_name}.avi', codec, fps, frame_size)

while(True):
	ret, img = cap.read()
	if not ret:
		break
	has_face = tracker.update(img)
	# PID更新
	if has_face and tracker.last_center is not None:
		face_center = tracker.last_center
		update_gimbal_pid()
	else:
		face_center = (IMG_WIDTH/2, IMG_HEIGHT/2)
			
	cv2.imshow('image_win', tracker.canvas)

	# 录像
	if IS_RECORD_FACE and  tracker.last_roi is not None:
		x, y, w, h = tracker.last_roi
		# print(f"w = {w} h = {h}")
		face_img = img[y:y+h, x:x+w]
		face_img = cv2.resize(face_img, frame_size)
		out.write(face_img)
	
  
	# 等待按键事件发生 等待1ms
	key = cv2.waitKey(1)
	if key == ord('q'):
		# 如果按键为q 代表quit 退出程序
		print("程序正常退出...Bye 不要想我哦")
		break
	
# 释放VideoCapture
cap.release()
# 销毁所有的窗口
cv2.destroyAllWindows()
# 视频保存释放
if IS_RECORD_FACE:
	out.release()