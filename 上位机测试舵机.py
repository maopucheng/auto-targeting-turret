import cv2
from cvzone.PoseModule import PoseDetector
from cvzone import FPS
import socket
import mtools


def main():
    # 获取视频高和宽，舵机初始角度
    global angle_down, angle_up
    send_servo_angle(angle_down, angle_up)
    while True:
        angle_down, angle_up = [int(i) for i in input("输入下(水平)上（垂直）角度：").split()]
        send_servo_angle(angle_down, angle_up)


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

    # 记录舵机云台位置,设置默认角度
    angle_down = 90  # 水平
    angle_up = 120  # 仰角

    # 执行主程序
    main()

    # 关闭各种资源
    skt.close()
    cap.release()
    cv2.destroyAllWindows()
