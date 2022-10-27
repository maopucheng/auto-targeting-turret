import cv2
import numpy as np
import mtools

# 简单说明
# https://blog.csdn.net/Kukeoo/article/details/116328341

img = cv2.imread("333.jpg")
imgContour = img.copy()

img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

canny = cv2.Canny(img, 150, 200)
# 2内外轮廓，3是否压缩
contours, hierarchy = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

for cnt in contours:
    # print(cnt)
    # 2轮廓点，3画哪些轮廓点，全部为-1，4颜色，5粗度
    cv2.drawContours(imgContour, cnt, -1, (255, 0, 0), 4)
    # 轮廓面积
    area = cv2.contourArea(cnt)
    # 忽略小的图形，避免噪点
    if area > 1000:
        # 轮廓边长，2为是否闭合为布尔值
        peri = cv2.arcLength(cnt, True)
        # 近似多边形的顶点，2近似值，3是否闭合
        vertices = cv2.approxPolyDP(cnt, peri * 0.02, True)
        # 形状的顶点数量
        corners = len(vertices)
        # 把形状框出来,并通过顶点数进行判断和标注
        x, y, w, h = cv2.boundingRect(vertices)
        cv2.rectangle(imgContour, (x, y), (x + w, y + h), (0, 255, 0), 4)
        if corners == 3:
            cv2.putText(
                imgContour,
                "triangle",
                (x, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2,
            )
        elif corners == 4:
            cv2.putText(
                imgContour,
                "rectangle",
                (x, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2,
            )
        elif corners == 5:
            cv2.putText(
                imgContour,
                "pentagon",
                (x, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2,
            )
        elif corners >= 6:
            cv2.putText(
                imgContour,
                "circle",
                (x, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2,
            )

cv2.imshow("img", img)
cv2.imshow("canny", canny)
cv2.imshow("imgContour", imgContour)
cv2.waitKey(10000)
