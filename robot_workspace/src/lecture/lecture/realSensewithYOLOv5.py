# -*- coding: utf-8 -*-
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

import cv2
import numpy as np
import pyrealsense2 as rs
import torch

from collections import Counter

class RealSenseYoloNode(Node):
    def __init__(self):
        super().__init__('realsense_yolov5_node')

        # YOLOv5 custom 모델 로드
        self.yolo_model = torch.hub.load(
            'ultralytics/yolov5',
            'custom',
            path='/home/ssafy/pjt9_ws/src/lecture/yolov5_model/best.pt',
            force_reload=False
        )

        # RealSense 설정
        self.pipeline = rs.pipeline()
        cfg = rs.config()
        cfg.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        self.pipeline.start(cfg)

        # ROS 퍼블리셔
        self.detection_publisher = self.create_publisher(String, 'detection_results', 10)
        self.image_publisher     = self.create_publisher(Image,  'detection_image',   10)
        self.bridge = CvBridge()

        # 색상 안정화용 버퍼
        self.color_buffer = []
        self.color_buffer_size = 5    # 최근 5프레임 저장
        self.color_threshold   = 3    # 3프레임 이상 일치 시 확정

        # 타이머 (0.1초 주기)
        self.timer = self.create_timer(0.1, self.timer_callback)

    def get_center_color(self, image):
        """
        ROI 내부 픽셀들의 HSV 값을 median 으로 계산합니다.
        """
        h, w = image.shape[:2]
        cy, cx = h//2, w//2
        sz = min(h, w)//4
        roi = image[cy-sz//2:cy+sz//2, cx-sz//2:cx+sz//2]
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        median_hsv = np.median(hsv.reshape(-1, 3), axis=0)
        return median_hsv

    def get_color_name(self, hsv_color, label):
        """
        HSV median 값을 기반으로 색상 판정.
        label 에 따라 화이트 기준을 다르게 적용합니다.
        """
        h, s, v = map(int, hsv_color)
        # 디버깅용 로그
        self.get_logger().info(f"[DEBUG] ({label}) HSV median = H:{h}, S:{s}, V:{v}")

        # board_panel 기본 화이트 기준
        if v >= 120 and s <= 150:
            return 'white'
        # back_panel 전용 화이트 기준 (좀 더 느슨하게)
        if label == 'back_panel' and v >= 120 and s <= 150:
            return 'white'

        # 빨간색
        if (h <= 15 or h >= 160) and s >= 120 and v >= 80:
            return 'red'
        # 파란색
        if 90 <= h <= 140 and s >= 100 and v >= 50:
            return 'blue'

        return 'unknown'

    def timer_callback(self):
        frames = self.pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        if not color_frame:
            return

        img = np.asanyarray(color_frame.get_data())
        results = self.yolo_model(img)

        detections = String()

        if len(results.xyxy[0]) > 0:
            # 첫 번째 검출 객체만 처리
            *box, conf, cls = results.xyxy[0][0].cpu().numpy()
            x1, y1, x2, y2 = map(int, box)
            label = self.yolo_model.names[int(cls)]
            roi = img[y1:y2, x1:x2]

            # HSV median → 색상 이름 판정 (label별 기준)
            hsv_med = self.get_center_color(roi)
            detected_color = self.get_color_name(hsv_med, label)

            # 버퍼에 추가 후 오래된 건 제거
            self.color_buffer.append(detected_color)
            if len(self.color_buffer) > self.color_buffer_size:
                self.color_buffer.pop(0)

            # 최빈색 계산
            most_common, count = Counter(self.color_buffer).most_common(1)[0]
            stable_color = (most_common
                            if (most_common != 'unknown' and count >= self.color_threshold)
                            else 'unknown')

            # 시각화
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                img,
                f"{label}-{stable_color}",
                (x1, y1-10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (0, 255, 0), 2
            )

            detections.data = f"{label} {stable_color}"
        else:
            # 검출 없으면 버퍼 초기화
            self.color_buffer.clear()
            detections.data = ""

        # 퍼블리시
        self.detection_publisher.publish(detections)
        img_msg = self.bridge.cv2_to_imgmsg(img, encoding='bgr8')
        self.image_publisher.publish(img_msg)

    def destroy_node(self):
        self.pipeline.stop()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = RealSenseYoloNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
