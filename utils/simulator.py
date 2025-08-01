import random
import time

import cv2
import numpy as np
import pyautogui
from PIL import ImageGrab


class MouseDragSimulator:
    """
    鼠标点击拖动轨迹模拟（贝塞尔曲线速率）
    """

    def __init__(self, duration=1.0, steps=50):
        self.duration = duration  # 总移动时间（秒）
        self.steps = steps  # 轨迹点数
        # 贝塞尔曲线控制点（用于速率变化）
        self.control_points = [
            (0.0, 0.0),
            (random.uniform(0.2, 0.4), random.uniform(0.3, 0.7)),
            (random.uniform(0.6, 0.8), random.uniform(0.3, 0.7)),
            (1.0, 1.0)
        ]

    def calculate_bezier_progress(self, t):
        """计算贝塞尔曲线在t时刻的进度值（0-1之间）"""
        # 解压控制点
        p0, p1, p2, p3 = self.control_points

        # 三次贝塞尔曲线公式
        mt = 1 - t
        x = (mt ** 3 * p0[0] +
             3 * mt ** 2 * t * p1[0] +
             3 * mt * t ** 2 * p2[0] +
             t ** 3 * p3[0])

        y = (mt ** 3 * p0[1] +
             3 * mt ** 2 * t * p1[1] +
             3 * mt * t ** 2 * p2[1] +
             t ** 3 * p3[1])

        return y  # 返回y值作为进度百分比

    def generate_movement_trajectory(self, start_pos, end_pos):
        """
        生成直线路径，但移动速率按贝塞尔曲线变化
        :param start_pos: 起始位置 (x, y)
        :param end_pos: 目标位置 (x, y)
        :return: 轨迹点列表 [(x1, y1), (x2, y2), ...]
        """
        points = []
        sx, sy = start_pos
        ex, ey = end_pos

        # 计算总位移
        dx = ex - sx
        dy = ey - sy

        # 生成路径点（直线）
        for i in range(self.steps + 1):
            t = i / self.steps
            # 获取贝塞尔曲线决定的进度
            progress = self.calculate_bezier_progress(t)
            # 计算当前位置（直线移动）
            x = sx + dx * progress
            y = sy + dy * progress
            points.append((x, y))

        return points

    def drag(self, start_pos, end_pos):
        path = self.generate_movement_trajectory(start_pos, end_pos)
        pyautogui.moveTo(*start_pos)  # 移动鼠标到起始位置
        pyautogui.mouseDown()  # 按下鼠标

        interval = self.duration / self.steps
        for i in range(1, len(path)):
            # 添加随机延迟使移动更自然
            delay = interval * random.uniform(0.8, 1.2)
            pyautogui.moveTo(*path[i])
            time.sleep(delay)

        pyautogui.mouseUp()  # 释放鼠标


class VisionClickSimulator:
    def __init__(self, match_threshold=0.8, click_delay=0.5):
        """
        视觉自动化点击模拟器
        :param match_threshold: 默认图像匹配阈值 (0-1)
        :param click_delay: 默认点击前延迟(秒)
        """
        self.match_threshold = match_threshold
        self.click_delay = click_delay
        self.last_detected_position = None  # 最后检测到的位置缓存

        # 获取屏幕截图
        self.screenshot = self._capture_screen()

    def _capture_screen(self):
        """
        捕获屏幕并返回PIL图像对象
        捕获当前屏幕并转换为OpenCV格式
        :return:
        """
        return ImageGrab.grab()

    def _convert_pil_to_opencv(self, pil):
        """
        将PIL图像转换为OpenCV格式
        :param pil: PIL图像对象
        :return: OpenCV格式的图像
        """
        # 转换颜色空间 RGB to BGR
        return cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)


    def locate_image(self, template_path, threshold=None):
        """
        在屏幕上定位目标图像
        :param template_path: 模板图片路径
        :param threshold: 匹配阈值 (0-1)，默认使用初始化值
        :return: 匹配区域的中心坐标 (x, y)，未找到返回None
        """
        # 使用类默认阈值
        if threshold is None:
            threshold = self.match_threshold

        # 读取模板图像
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        if template is None:
            raise FileNotFoundError(f"模板图片未找到: {template_path}")

        screen = self._convert_pil_to_opencv(self.screenshot)

        # 模板匹配
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # 检查匹配结果
        if max_val < threshold:
            return None

        # 计算中心坐标
        height, width = template.shape[:2]
        top_left = max_loc
        center_x = top_left[0] + width // 2
        center_y = top_left[1] + height // 2

        self.last_detected_position = (center_x, center_y)
        return center_x, center_y

    def click_target(self, template_path=None, threshold=None, delay=None):
        """
        点击屏幕上的目标
        :param template_path: 模板图片路径
        :param threshold: 匹配阈值
        :param delay: 点击前延迟(秒)
        :return: 成功点击返回True，否则False
        """
        # 设置延迟
        wait_time = delay if delay is not None else self.click_delay

        # 模板匹配模式
        if template_path is None:
            raise ValueError("必须提供template_path参数")

        target_position = self.locate_image(template_path, threshold)

        if target_position:
            print(f"定位到目标，坐标: {target_position}")
            time.sleep(wait_time)
            pyautogui.click(target_position[0], target_position[1])
            print("点击操作完成")
            return True

        print("未找到目标图像")
        return False

    def _click_position(self, position=None, delay=None):
        """
        鼠标点击目标位置
        :param position: 直接指定点击位置 (x, y)
        :param delay: 点击前延迟(秒)
        :return:
        """
        # 设置延迟
        wait_time = delay if delay is not None else self.click_delay

        # 直接点击模式
        if position is not None:
            time.sleep(wait_time)
            pyautogui.click(position[0], position[1])
            print(f"点击指定位置: {position}")
            return True

    def repeat_last_click(self, delay=None):
        """重复点击上一次定位到的位置"""
        if self.last_detected_position is None:
            print("没有可用的位置缓存")
            return False
        return self._click_position(position=self.last_detected_position, delay=delay)


if __name__ == "__main__":
    # time.sleep(2)  # 等待两秒，用于切换到目标窗口/激活目标窗口
    # simulator = MouseDragSimulator(duration=1.5, steps=60)
    # simulator.drag((500, 500), (800, 500))

    # 初始化点击器
    automator = VisionClickSimulator(match_threshold=0.85, click_delay=1.0)
    # 通过图像定位并点击
    automator.click_target("submit_button.png")
    # 重复上次点击
    automator.repeat_last_click()
    # 自定义参数点击
    automator.click_target("special_icon.png", threshold=0.9, delay=2.0)
