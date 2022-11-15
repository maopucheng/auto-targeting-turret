import cv2
import mtools

img = cv2.imread("444.jpg")
img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

faceCascade = cv2.CascadeClassifier("face_detect.xml")
# 2每一轮缩小倍数，3最少要框到几次才能算成功
faceRect = faceCascade.detectMultiScale(gray, 1.1, 6)

for (x, y, w, h) in faceRect:

cv2.imshow("img", img)
cv2.waitKey(10000)
