import cv2
from cvzone.PoseModule import PoseDetector
import cvzone

fpsReader = cvzone.FPS()
detector = PoseDetector()
cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    # img = cv2.flip(img, 180)
    fps, img = fpsReader.update(
        img, pos=(50, 80), color=(0, 255, 0), scale=5, thickness=5
    )
    # 寻找身体
    img = detector.findPose(img)
    lmList, bboxInfo = detector.findPosition(img, bboxWithHands=False)
    if bboxInfo:
        # bboxInfo - "id","bbox","score","center"
        center = bboxInfo["center"]
        cv2.circle(img, center, 5, (255, 0, 255), cv2.FILLED)
    cv2.imshow("Result", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()

cv2.destroyAllWindows()


# https://learnopencv.com/object-tracking-using-opencv-cpp-python/ 脸部追踪
# https://blog.csdn.net/weixin_53403301/article/details/120497427 另一个
