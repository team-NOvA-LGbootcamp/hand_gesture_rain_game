import tflite_runtime.interpreter as tflite
import numpy as np
import time
import cv2
from mediapipe import solutions

class HandGestureRecognition:
    def __init__(self, model_path, camera_index=0):
        self.model_path = model_path
        self.interpreter = tflite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.input_dtype = self.input_details[0]['dtype']
        self.ansToText = 'ABFVY'
        self.IMG_SIZE = 28
        self.offset = 15
        self.CAM_WIDTH = 320
        self.CAM_HEIGHT = 240
        self.CAM_BUFFERSIZE = 1
        self.FONT_SCALE = 2
        self.FONT_THICKNESS = 2
        self.RECTANGLE_COLOR = [(0, 0, 255),(255,0,0)]
        self.TEXT_COLOR = [(0, 0, 255),(255,0,0)]
        self.FPS_COLOR = (0, 255, 255)
        self.FPS_POSITION = (20, 50)
        self.CAP_PROP_FRAME_WIDTH = cv2.CAP_PROP_FRAME_WIDTH
        self.CAP_PROP_FRAME_HEIGHT = cv2.CAP_PROP_FRAME_HEIGHT
        self.CAP_PROP_BUFFERSIZE = cv2.CAP_PROP_BUFFERSIZE
        self.FONT = cv2.FONT_HERSHEY_PLAIN
        self.FPS_ROUND_DECIMALS = 1
        self.cap = cv2.VideoCapture(camera_index)
        self.cap.set(self.CAP_PROP_FRAME_WIDTH, self.CAM_WIDTH)
        self.cap.set(self.CAP_PROP_FRAME_HEIGHT, self.CAM_HEIGHT)
        self.cap.set(self.CAP_PROP_BUFFERSIZE, self.CAM_BUFFERSIZE)
        self.startTime = 0
        self.ans = -1
        self.cam_frame = None
        self.prob= 0 
        self.threshold = 0.7

        # Mediapipe 손 추적 모듈 초기화
        self.mp_hands = solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False, 
            max_num_hands=1,
            model_complexity=0, 
            min_detection_confidence=0.5, 
            min_tracking_confidence=0.5
        )

    def get_hand(self, frame):
        results = self.hands.process(frame)
        if results.multi_hand_landmarks:
            h, w, _ = frame.shape
            hand_landmarks = results.multi_hand_landmarks[0].landmark
            x_coords = [int(lm.x * w) for lm in hand_landmarks]
            y_coords = [int(lm.y * h) for lm in hand_landmarks]
            return min(x_coords), min(y_coords), max(x_coords), max(y_coords)
        return None

    def process_image(self, frame):
        bbox = self.get_hand(frame)
        if bbox is None:
            self.ans = -1
            return
        x1, y1, x2, y2 = bbox
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        w = x2 - x1
        h = y2 - y1
        line = max(w, h)
        x1, y1 = center_x - line // 2 - self.offset, center_y - line // 2 - self.offset
        x2, y2 = center_x + line // 2 + self.offset, center_y + line // 2 + self.offset

        # 범위 초과 확인
        if x1 < 0 or y1 < 0 or x2 > self.CAM_WIDTH or y2 > self.CAM_HEIGHT:
            return

        # 손만 떼어오기
        img = frame[y1:y2, x1:x2]

        # BGR을 RGB로 변경
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = img / 255.0
        img = cv2.resize(img, (self.IMG_SIZE, self.IMG_SIZE))

        img = np.expand_dims(img, -1)
        img = np.expand_dims(img, 0)

        self.interpreter.set_tensor(self.input_details[0]['index'], img.astype(self.input_dtype))
        self.interpreter.invoke()
        output_data = self.interpreter.get_tensor(self.output_details[0]['index'])[0]
        self.prob = np.max(output_data)
        self.ans = np.argmax(output_data)
        text = f'{self.ansToText[self.ans]}:{self.prob*100:.1f}%' if self.prob >= self.threshold else f'{self.prob*100:.1f}%'
        cv2.rectangle(frame, (x1, y1), (x2, y2), self.RECTANGLE_COLOR[0] if self.prob >= self.threshold else self.RECTANGLE_COLOR[1], 2)
        cv2.putText(frame, text, (x1, y1 - 7), self.FONT, self.FONT_SCALE, self.TEXT_COLOR[0] if self.prob >= self.threshold else self.TEXT_COLOR[1], self.FONT_THICKNESS)


    def run(self, stop_event):
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
            curTime = time.time()
            fps = 1 / (curTime - self.startTime)
            self.startTime = curTime
            self.process_image(frame)
            # cv2.putText(frame, f'FPS: {fps:.{self.FPS_ROUND_DECIMALS}f}', self.FPS_POSITION, self.FONT, self.FONT_SCALE, self.FPS_COLOR, self.FONT_THICKNESS)
            # cv2.imshow('img',frame)
            self.cam_frame = frame
            key = cv2.waitKey(10)
            if key == ord('q') or stop_event.is_set():
                break
        self.cap.release()
        cv2.destroyAllWindows()

    def get_ans(self):
        if self.prob >= self.threshold:
            return self.ans
        else:
            return -1

    def get_frame(self):
        return self.cam_frame
