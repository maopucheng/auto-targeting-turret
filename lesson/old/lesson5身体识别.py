import cv2
import mtools

img = cv2.imread("6xingren.jpg")
# img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

faceCascade = cv2.CascadeClassifier("upperbody_detect.xml")
# 2每一轮缩小倍数，3最少要框到几次才能算成功
faceRect = faceCascade.detectMultiScale(gray, 1.1, 1)

for (x, y, w, h) in faceRect:
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

cv2.imshow("img", img)
cv2.waitKey(10000)
