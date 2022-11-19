'''
云台串口通信
----------------------------
作者: 阿凯爱玩机器人
微信: xingshunkai
邮箱: xingshunkai@qq.com
更新日期: 2022/03/03
'''
import serial

# 云台串口配置
GIMBAL_UART_PORT =  'COM5' # 舵机串口号
GIMBAL_UART_BAUDRATE = 115200 # 舵机的波特率

# 初始化串口
gimbal_uart = serial.Serial(port=GIMBAL_UART_PORT, baudrate=GIMBAL_UART_BAUDRATE,\
					parity=serial.PARITY_NONE, stopbits=1,\
					bytesize=8,timeout=0)

# 设置舵机角度
def set_gimbal_raw_angle(angle_down, angle_up):
	gimbal_uart.write("{},{}\n".format(angle_down, angle_up).encode("utf-8"))