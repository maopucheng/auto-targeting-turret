import cv2
from cvzone.PoseModule import PoseDetector
import cvzone
import os
import json
import mtools


def target_position(keyList, target="heart"):

    target_pos = (0, 0)
    if target == "heart":
        # 设置瞄准点在胸部位置
        # 11，12，肩膀2个点，23，24为臀部外侧2个点
        shoulder_mid = (
            (keyList[11][1] + keyList[12][1]) / 2,
            (keyList[11][2] + keyList[12][2]) / 2,
        )
        hip_mid = (
            (keyList[23][1] + keyList[24][1]) / 2,
            (keyList[23][2] + keyList[24][2]) / 2,
        )
        heart_pos = (
            int(shoulder_mid[0] + (hip_mid[0] - shoulder_mid[0]) * 0.2),
            int(shoulder_mid[1] + (hip_mid[1] - shoulder_mid[1]) * 0.2),
        )
        target_pos = heart_pos
    elif target == "head":
        # 设置为眉心
        # 0 为鼻子，2，5为右左眼睛
        nose = keyList[0][1:3]
        eye_mid = (
            int((keyList[2][1] + keyList[5][1]) / 2),
            int((keyList[2][2] + keyList[5][2]) / 2),
        )
        brow_mid = (
            int(eye_mid[0] - (nose[0] - eye_mid[0]) * 1.5),
            int(eye_mid[1] - (nose[1] - eye_mid[1]) * 1.5),
        )
        target_pos = brow_mid
    return target_pos


def draw_target_center(img, aim_center):
    cv2.circle(img, aim_center, 5, (0, 0, 255), 2)
    cv2.circle(img, aim_center, 10, (0, 0, 255), 1)
    cv2.circle(img, aim_center, 15, (0, 0, 255), 1)
    cv2.line(
        img,
        (aim_center[0] - 25, aim_center[1]),
        (aim_center[0] + 25, aim_center[1]),
        (0, 0, 255),
        1,
    )
    cv2.line(
        img,
        (aim_center[0], aim_center[1] - 25),
        (aim_center[0], aim_center[1] + 25),
        (0, 0, 255),
        1,
    )
    # return img


def calc_servo_angle(aim_center):

    global angle_down
    global angle_up
    px, py = aim_center

    # 设置死区，在此范围内，不动作
    deadarea = 0.15

    # 比例系数，需要测试
    k_down = 8
    k_up = 6
    # 归一化 偏移量 [-1, 1]
    # offset_x +=  0.1*(2.0*(0.5 - px / IMG_WIDTH) - offset_x)
    offset_x = 2.0 * (px / width - 0.5)
    offset_y = 2.0 * (py / height - 0.5)

    if abs(offset_x) > deadarea:
        # 更新底部舵机的PID
        angle_down += k_down * offset_x
        if angle_down < 0:
            angle_down = 0
        elif angle_down > 180:
            angle_down = 180

    if abs(offset_y) > deadarea:
        # 更新上舵机的PID
        angle_up += k_up * offset_y
        # if angle_up < 0:
        #     angle_up = 0
        # elif angle_up > 90:
        #     angle_up = 90

    # 设置舵机角度
    set_servo_angle(angle_down, angle_up)
    print(
        "{:.2f},{:.2f},{:.0f},{:.0f}".format(offset_x, offset_y, angle_down, angle_up)
    )
    return (angle_down, angle_up)


def set_servo_angle(down, up):
    pass


fpsReader = cvzone.FPS()
detector = PoseDetector(complexity=0)
cap = cv2.VideoCapture(1)
pose_dict = {}

# 取得视频分辨率
success, img = cap.read()
if success:
    height, width = img.shape[:2]
    print(type(img))

while True:
    success, img = cap.read()
    # 屏幕镜像
    img = cv2.flip(img, 180)
    # 显示fps
    fps, img = fpsReader.update(
        img, pos=(50, 80), color=(0, 255, 0), scale=5, thickness=5
    )

    # # 复制一个图像，用于不需要关节显示的时候
    # img2 = img.copy()

    # 记录舵机云台位置,设置默认角度
    angle_down = 90  # 水平
    angle_up = 120  # 仰角

    # 寻找身体，检测位置
    img = detector.findPose(img)
    lmList, bboxInfo = detector.findPosition(img, bboxWithHands=False)
    if bboxInfo:
        aim_center = target_position(lmList, "heart")
        calc_servo_angle(aim_center)
        draw_target_center(img, aim_center)

    cv2.imshow("Result", img)

    # 按q退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
