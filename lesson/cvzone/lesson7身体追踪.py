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
    # 寻找身体
    img = detector.findPose(img)
    lmList, bboxInfo = detector.findPosition(img, bboxWithHands=False)
    if bboxInfo:
        # bboxInfo - "id","bbox","score","center"
        center = bboxInfo["center"]
        left_shoulder = (lmList[11][1], lmList[11][2])
        right_shoulder = (lmList[12][1], lmList[12][2])
        shoulder_center = (
            int((lmList[11][1] + lmList[12][1] + lmList[23][1] + lmList[24][1]) / 4),
            int((lmList[11][2] + lmList[12][2] + lmList[23][2] + lmList[24][2]) / 4),
        )
        cv2.circle(img, shoulder_center, 5, (255, 0, 255), cv2.FILLED)

        # for lm in lmList:
        #     pose_dict[lm[0]] = (lm[1], lm[2])

        # if not os.path.exists('result'):
        #     os.path.makedirs('result')
        # jsonFile_name = 'result/{}帧'.format(read_frame) + '.json'
        # json_file = open(jsonFile_name, 'w')
        # json_data = json.dumps(pose_dict)
        # json_file.write(json_data)
        # json_file.write('\n')
        # json_file.close()

    cv2.imshow("Result", img)

    if cv2.waitKey(100) & 0xFF == ord('q'):
        break

cap.release()

cv2.destroyAllWindows()


# https://learnopencv.com/object-tracking-using-opencv-cpp-python/ 脸部追踪
# https://blog.csdn.net/weixin_53403301/article/details/120497427 另一个
