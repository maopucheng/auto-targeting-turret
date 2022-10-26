import cv2
import numpy as np
import mtools

# # 通过numpy创建一张图
# img = np.zeros((300, 500, 3), np.uint8)

# # 画图参数：图，坐标，颜色，粗度或者填充
# cv2.line(img, (0, 0), (img.shape[1], img.shape[0]), (255, 0, 0), 2)
# cv2.rectangle(img, (0, 0), (100, 100), (0, 255, 0), 2)
# cv2.rectangle(img, (0, 0), (100, 100), (0, 255, 0), cv2.FILLED)
# cv2.circle(img, (100, 100), 100, (0, 0, 255), 4)
# # 图，文字，坐标，字体，大小，颜色，粗度
# cv2.putText(
#     img, "HELLO WORLD!", (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2
# )

# cv2.imshow("img", img)
# cv2.waitKey(0)

# 读取图片
img = cv2.imread("111.jpg")
img = cv2.resize(img, (0, 0), fx=0.6, fy=0.6)

cv2.imshow("img", img)
cv2.waitKey(5000)
