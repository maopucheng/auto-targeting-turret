import cv2 as cv2
import numpy as np
import mtools

# 读取图片
img = cv2.imread("111.jpg")

# 修改尺寸，2种方法
# img = cv2.resize(img, (300, 300))
img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
# print(type(img))
# print(img.shape)

# # 切片切割图片，前面是Y，后面是X
# img2 = img[50:690, 50:700]

# 图形翻转，0垂直，1水平，-1两个都要
img2 = cv2.flip(img, 0)

# # 将图片转成灰度图
# gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# # 高斯模糊，第2个参数，核大小的元组必须都是奇数，第3参数，标准差
# blur = cv2.GaussianBlur(img, (15, 15), 15)

# 取得图片的边缘,2最低门槛值，3为最高门槛，与周围像素差异越大越高
canny = cv2.Canny(img, 200, 250)

# 膨胀图片边缘
kernel = np.ones((5, 5), np.uint8)
kernel2 = np.ones((5, 5), np.uint8)
print(kernel)
# 1图片，2kernel，3膨胀次数
dilate = cv2.dilate(canny, kernel, iterations=3)
# 1图片，2kernel，3收缩次数
erode = cv2.erode(dilate, kernel2, iterations=1)

# cv2.imshow("img", img)
# cv2.imshow("img2", img2)
# # cv2.imshow("gray", gray)
# # cv2.imshow("blur", blur)
cv2.imshow("canny", canny)
cv2.imshow("dilate", dilate)
# cv2.imshow("erode", erode)

# 显示后等待关闭时间，单位毫秒
cv2.waitKey(10000)

# # 处理视频

# # 读取视频文件
# cap = cv2.VideoCapture("aaa.mp4")

# # 读取摄像头，一般从0开始编号
# cap = cv2.VideoCapture(0)

# while True:
#     # 读取每一帧，ret为是否成功的布尔值，frame为该帧的图像
#     ret, frame = cap.read()

#     if ret:
#         # 取得图片的边缘,2最低门槛值，3为最高门槛，与周围像素差异越大越高
#         canny = cv2.Canny(frame, 100, 160)
#         cv2.imshow("video", canny)
#     else:
#         break
#     if cv2.waitKey(1) == ord(" "):
#         break
