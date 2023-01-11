import cv2
from cvzone.PoseModule import PoseDetector
from cvzone import FPS
import socket
import mtools
import time


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

    global angle_down, angle_up, width, height
    # print("global:", int(angle_down), int(angle_up), width, height)
    px, py = aim_center

    # 设置死区，在此范围内，不动作
    deadarea = 0.15

    # 比例系数，需要测试
    k_down = 6
    k_up = 4
    # 归一化 偏移量 [-1, 1]
    offset_x = 2.0 * (px / width - 0.5)
    offset_y = 2.0 * (py / height - 0.5)

    if abs(offset_x) > deadarea:
        # 更新底部舵机的PID，转角0-180
        angle_down += int(k_down * offset_x)
        if angle_down < 0:
            angle_down = 0
        elif angle_down > 180:
            angle_down = 180

    if abs(offset_y) > deadarea:
        # 更新上舵机的PID，设置仰角80-160
        # 注意，这里用了-号，因为图像左右镜像过，所以正负需要颠倒。
        angle_up -= int(k_up * offset_y)
        if angle_up < 80:
            angle_up = 80
        elif angle_up > 160:
            angle_up = 160

    # # 返回舵机角度
    # print(
    #     "{:.2f},{:.2f},{:.0f},{:.0f}".format(offset_x, offset_y, angle_down, angle_up)
    # )

    time.sleep(0.01)

    return (angle_down, angle_up)


def main():
    # 获取视频高和宽，舵机初始角度
    global angle_down, angle_up, width, height

    # 初始化FPS，detector和视频流
    fpsReader = FPS()
    detector = PoseDetector()

    # 取得视频分辨率
    success, img = cap.read()
    if success:
        height, width = img.shape[:2]
        print("视频流的分辨率为：{}X{}".format(width, height))

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

        # 寻找身体，检测位置
        img = detector.findPose(img)
        lmList, bboxInfo = detector.findPosition(img, bboxWithHands=False, draw=True)
        if bboxInfo:
            aim_center = target_position(lmList, "head")
            draw_target_center(img, aim_center)
            angle_down, angle_up = calc_servo_angle(aim_center)
            # 发送舵机角度信息到执行器
            send_servo_angle(angle_down, angle_up)

        cv2.imshow("Result", img)

        # 按q退出
        if cv2.waitKey(40) & 0xFF == ord('q'):
            break


# 启动一个socket，发送socket
def send_servo_angle(angle_down, angle_up):
    send_data = str(angle_down) + ',' + str(angle_up) + '#'
    print("send data: " + send_data)
    skt.send(send_data.encode())


if __name__ == "__main__":

    # 设置执行器的地址和端口，一般是个元组
    ip = ('192.168.1.51', 1080)

    # 初始化一个socket客户端
    skt = socket.socket()
    skt.settimeout(10)
    try:
        print("连接到执行器 {}:{} ......".format(ip[0], ip[1]))
        skt.connect(ip)
        print("连接成功！")
    except Exception as err:
        print("socket出错：", err)
        exit()

    # 初始化视频流
    cap = cv2.VideoCapture(1)

    # 记录舵机云台位置,设置默认角度
    angle_down = 90  # 水平
    angle_up = 100  # 仰角

    # 视频的尺寸初始化
    width = 640
    height = 480

    # 执行主程序
    main()

    # 关闭各种资源
    skt.close()
    cap.release()
    cv2.destroyAllWindows()
