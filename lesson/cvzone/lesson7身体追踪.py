import cv2
from cvzone.PoseModule import PoseDetector
import cvzone
import os
import json
import mtools

fpsReader = cvzone.FPS()
detector = PoseDetector()
cap = cv2.VideoCapture(0)
pose_dict = {}

while True:
    success, img = cap.read()
    img = cv2.flip(img, 180)
    fps, img = fpsReader.update(
        img, pos=(50, 80), color=(0, 255, 0), scale=5, thickness=5
    )
    img2 = img.copy()
    # 寻找身体
    img2 = detector.findPose(img)
    lmList, bboxInfo = detector.findPosition(img, bboxWithHands=False)
    if bboxInfo:
        # bboxInfo - "id","bbox","score","center"
        center = bboxInfo["center"]
        # 11，12，肩膀2个点，23，24为臀部外侧2个点
        # 设置瞄准点在胸部位置
        shoulder_mid = (
            (lmList[11][1] + lmList[12][1]) / 2,
            (lmList[11][2] + lmList[12][2]) / 2,
        )
        hip_mid = (
            (lmList[23][1] + lmList[24][1]) / 2,
            (lmList[23][2] + lmList[24][2]) / 2,
        )
        body_center = (
            int(shoulder_mid[0] + (hip_mid[0] - shoulder_mid[0]) * 0.2),
            int(shoulder_mid[1] + (hip_mid[1] - shoulder_mid[1]) * 0.2),
        )
        cv2.circle(img2, body_center, 5, (0, 0, 255), 2)
        cv2.circle(img2, body_center, 10, (0, 0, 255), 2)
        cv2.circle(img2, body_center, 15, (0, 0, 255), 2)
        cv2.line(
            img2,
            (body_center[0] - 25, body_center[1]),
            (body_center[0] + 25, body_center[1]),
            (0, 0, 255),
            2,
        )
        cv2.line(
            img2,
            (body_center[0], body_center[1] - 25),
            (body_center[0], body_center[1] + 25),
            (0, 0, 255),
            2,
        )

    cv2.imshow("Result", img2)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()

cv2.destroyAllWindows()


# https://learnopencv.com/object-tracking-using-opencv-cpp-python/ 脸部追踪
# https://blog.csdn.net/weixin_53403301/article/details/120497427 另一个
