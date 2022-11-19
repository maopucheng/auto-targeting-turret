'''
自动进行阈值调节, 获取目标颜色的颜色签名(参照Pixy的学习功能)
----------------------------
作者: 阿凯爱玩机器人
微信: xingshunkai
邮箱: xingshunkai@qq.com
更新日期: 2022/03/03
'''
import os
import cv2
import numpy as np
import json
# from matplotlib import pyplot as plt

class ColorSignature:
    '''颜色签名'''
    CONTOUR_WIDTH_TAG_MIN_W = 40
    # 标签的尺寸
    TAG_WIDTH = 50 # 其实可以根据字符个数动态调整
                    # 20 * N
    TAG_HEIGHT = 25

    def __init__(self, name="颜色名称", color=(255, 255, 255)):
        self.name = name # 颜色的名字
        self.color = color # 在画布上的绘制的颜色
        # H通道的阈值(Hue 色相)
        self.h_min = 0
        self.h_max = 0
        self.h_mean = 0
        # S通道的阈值 (饱和度)
        self.s_min = 0
        self.s_max = 0
        self.s_mean = 0
    
    def binary(self, img_bgr):
        '''图像二值化'''
        img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        img_bin = cv2.inRange(img_hsv, lowerb=(self.h_min, self.s_min, 0), upperb=(self.h_max, self.s_max, 255))
        # 膨胀一下获得更好的效果
        img_bin = cv2.dilate(img_bin, np.ones((5, 5)))
        img_bin = cv2.erode(img_bin, np.ones((3, 3)))
        img_bin = cv2.dilate(img_bin, np.ones((3, 3)))
        img_bin = cv2.erode(img_bin, np.ones((3, 3)))
        return img_bin

    def binary_with_color(self, img_bgr=None, binary=None):
        '''将二值化图像赋值为带颜色的图像'''
        # 获取二值化图像
        if binary is None:
            img_bin = self.binary(img_bgr)
        img_h, img_w = img_bin.shape
        # 创建纯色背景
        background = np.zeros_like(img_bgr)
        background[:, :] = self.color
        # 使用Mask抠图
        return cv2.bitwise_and(background, background, mask=img_bin)
    
    def find_contours(self, img_bgr, canvas=None):
        '''在彩图上标注出识别到的物体以及名称标注(不过滤)'''
        # 准备画布
        if canvas is None:
            canvas = np.copy(img_bgr)
        # 二值化图像
        binary = self.binary(img_bgr)
        # 绘制画面中所有的连通域
        result = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours, hier = result[-2:] # 这么写是为了兼容opencv3
        rects = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            
            # 绘制名称(只在比较大的连通域上绘制)
            if w >= self.CONTOUR_WIDTH_TAG_MIN_W:
                # 添加矩形区域
                rects.append((x, y, w, h))
                # 绘制矩形
                cv2.rectangle(canvas, pt1=(x, y), pt2=(x+w, y+h),color=self.color, thickness=3)
                self.TAG_WIDTH = self.TAG_HEIGHT * len(self.name)
                cv2.rectangle(canvas, pt1=(x, y-self.TAG_HEIGHT), pt2=(x+self.TAG_WIDTH, y),color=self.color, thickness=-1)
                # 绘制标签
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(canvas, text=self.name, org=(x, y), fontFace=font, fontScale=1, thickness=2, lineType=cv2.LINE_AA, color=(255, 255, 255))
        
        return rects, canvas
    
    def save(self):
        '''保存颜色签名'''
        # 将数据保存转化为JSON格式并保存
        signature_dict = {}
        signature_dict['name'] = self.name
        signature_dict['color'] = self.color
        signature_dict['h_min'] = self.h_min
        signature_dict['h_max'] = self.h_max
        signature_dict['h_mean'] = self.h_mean
        signature_dict['s_min'] = self.s_min
        signature_dict['s_max'] = self.s_max
        signature_dict['s_mean'] = self.s_mean

        with open('data/color_signature/{}.json'.format(self.name), 'w') as f:
            f.write(json.dumps(signature_dict))
        
    def load(self, name):
        # 判断是否存在这个文件
        file_path = 'data/color_signature/{}.json'.format(name)
        if not os.path.exists(file_path):
            return False
        
        # 根据名字去载入
        signature_dict = None
        with open(file_path, 'r') as f:
            signature_dict = json.loads(f.read())
        # 填写数据
        self.name = signature_dict['name']
        self.color = signature_dict['color']
        self.h_min = signature_dict['h_min']
        self.h_max = signature_dict['h_max']
        self.h_mean = signature_dict['h_mean']
        self.s_min = signature_dict['s_min']
        self.s_max = signature_dict['s_max']
        self.s_mean = signature_dict['s_mean']
        return True
    def __str__(self):
        data_str = 'name={}, color={}'.format(self.name, self.color)
        data_str += 'h_min={}, h_max={}, h_mean={} \n'.format(self.h_min, self.h_max, self.h_mean)
        data_str += 's_min={}, s_max={}, s_mean={} \n'.format(self.s_min, self.s_max, self.s_mean)
        return data_str

class HSVThresholdAuto:
    '''自动获取HSV阈值'''
    RATIO = 0.9
    H_SCALAR = 1.1 # 1.5
    S_SCALAR = 1.1 # 1.4

    def __init__(self):
        # 目标区域的ROI图像
        self.roi_bgr = None # roi_bgr
        # 转换为hsv色彩空间W
        self.roi_hsv = None # cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2HSV)
        # HSV通道分离
        self.ch_h, self.ch_s, self.ch_v = None, None, None # cv2.split(self.roi_hsv)
        # 获取颜色签名
        self.signature = None # ColorSignature()

    def adjustValue(self, value, lowerb, upperb):
        '''调整数值'''
        if value < lowerb:
            return lowerb
        elif value > upperb:
            return upperb
        else:
            return value

    def adjust_h_min(self, scale):
        ratio = np.sum(self.ch_h >= self.signature.h_min) / self.ch_h.size
        if ratio < self.RATIO:
            self.signature.h_min -= scale
        else:
            self.signature.h_min += scale

        self.signature.h_min = self.adjustValue(self.signature.h_min, 0, 180)

    def adjust_h_max(self, scale):
        ratio = np.sum(self.ch_h <= self.signature.h_max) / self.ch_h.size
        if ratio < self.RATIO:
            self.signature.h_max += scale
        else:
            self.signature.h_max -= scale
        self.signature.h_max = self.adjustValue(self.signature.h_max, 0, 180)
    
    def adjust_s_min(self, scale):
        ratio = np.sum(self.ch_s >= self.signature.s_min) / self.ch_s.size
        if ratio < self.RATIO:
            self.signature.s_min -= scale
        else:
            self.signature.s_min += scale

        self.signature.s_min = self.adjustValue(self.signature.s_min, 0, 255)

    def adjust_s_max(self, scale):
        ratio = np.sum(self.ch_s <= self.signature.s_max) / self.ch_s.size
        if ratio < self.RATIO:
            self.signature.s_max += scale
        else:
            self.signature.s_max -= scale

        self.signature.s_max = self.adjustValue(self.signature.s_max, 0, 255)

    def learn(self, roi_bgr, signature):
        '''学习阈值调节'''
        # 先对原图做一个均值滤波
        # self.roi_bgr = cv2.medianBlur(np.copy(roi_bgr), 7)
        self.roi_bgr = np.copy(roi_bgr)
        # 转换为hsv色彩空间W
        self.roi_hsv = cv2.cvtColor(self.roi_bgr, cv2.COLOR_BGR2HSV)
        # HSV通道分离
        self.ch_h, self.ch_s, self.ch_v =  cv2.split(self.roi_hsv)
        self.signature = signature
        # TODO 这个数值搜索算法可以优化
        # 适合用凸优化来做
        for i in range(7, 0, -1):
            scale = 1 << i  # 缩放的尺度
            self.adjust_h_min(scale)
            self.adjust_h_max(scale)
            self.adjust_s_min(scale)
            self.adjust_s_max(scale)

        # 缩放范围
        self.signature.h_mean = np.mean(self.ch_h)
        self.signature.h_max = int(self.signature.h_mean + self.H_SCALAR * (self.signature.h_max - self.signature.h_mean))
        self.signature.h_max = self.adjustValue(self.signature.h_max, 0, 180)
        self.signature.h_min = int(self.signature.h_mean - self.H_SCALAR * (self.signature.h_mean - self.signature.h_min))
        self.signature.h_min = self.adjustValue(self.signature.h_min, 0, 180)
        self.signature.s_mean = np.mean(self.ch_s)
        self.signature.s_max = int(self.signature.s_mean + self.S_SCALAR * (self.signature.s_max - self.signature.s_mean))
        self.signature.s_max = self.adjustValue(self.signature.s_max, 0, 255)
        self.signature.s_min = int(self.signature.s_mean - self.S_SCALAR * (self.signature.s_mean - self.signature.s_min))
        self.signature.s_min = self.adjustValue(self.signature.s_min, 0, 255)

        return self.signature
