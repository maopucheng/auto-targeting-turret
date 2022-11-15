import cv2
import numpy as np
import mtools


def empty(v):
    pass


# # 读取图片
# img = cv2.imread("222.jpg")
# img = cv2.resize(img, (0, 0), fx=0.6, fy=0.6)

cap = cv2.VideoCapture(0)

# 创建一个跟踪窗口
h, w, = (
    300,
    400,
)
cv2.namedWindow("TrackBar")
cv2.resizeWindow("TrackBar", w, h)

# 创建控制条
cv2.createTrackbar("Hue Min", "TrackBar", 0, 179, empty)
cv2.createTrackbar("Hue Max", "TrackBar", 179, 179, empty)
cv2.createTrackbar("Sat Min", "TrackBar", 0, 255, empty)
cv2.createTrackbar("Sat Max", "TrackBar", 255, 255, empty)
cv2.createTrackbar("Val Min", "TrackBar", 0, 255, empty)
cv2.createTrackbar("Val Max", "TrackBar", 255, 255, empty)

# # 将RGB模式转换成HSV模式
# hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

while True:
    h_min = cv2.getTrackbarPos("Hue Min", "TrackBar")
    h_max = cv2.getTrackbarPos("Hue Max", "TrackBar")
    s_min = cv2.getTrackbarPos("Sat Min", "TrackBar")
    s_max = cv2.getTrackbarPos("Sat Max", "TrackBar")
    v_min = cv2.getTrackbarPos("Val Min", "TrackBar")
    v_max = cv2.getTrackbarPos("Val Max", "TrackBar")
    # print(h_min, h_max, s_min, s_max, v_min, v_max)

    # 将RGB模式转换成HSV模式
    ret, img = cap.read()
    # if ret:
    #     img = cv2.flip(img, 1)  # 翻转镜像

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower = np.array([h_min, s_min, v_min])
    upper = np.array([h_max, s_max, v_max])

    mask = cv2.inRange(hsv, lower, upper)

    # 测试bitwise函数，用另一种方法做掩码
    # mask_RGB = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    # print(img.shape, mask.shape, mask_RGB.shape)

    result = cv2.bitwise_and(img, img, mask=mask)

    cv2.imshow("img", img)
    # cv2.imshow("hsv", hsv)
    cv2.imshow("mask", mask)
    cv2.imshow("result", result)
    cv2.waitKey(5)
