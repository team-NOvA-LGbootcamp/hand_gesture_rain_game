import tflite_runtime.interpreter as tflite
import numpy as np
import time
import cv2
from cvzone.HandTrackingModule import HandDetector

class HandGestureRecognition:
    def __init__(self, model_path, camera_index=0):
        self.hd = HandDetector(maxHands=1)
        self.model_path = model_path
        self.interpreter = tflite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.input_dtype = self.input_details[0]['dtype']
        self.height = self.input_details[0]['shape'][1]
        self.width = self.input_details[0]['shape'][2]
        self.ansToText = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        self.IMG_SIZE = 28
        self.offset = 30
        self.cap = cv2.VideoCapture(camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.startTime = 0
        self.ans = None

    def process_image(self, frame):

        hands, _ = self.hd.findHands(frame, draw=False)
        if not hands: return

        x, y, w, h = hands[0]['bbox']
        center_x, center_y = x+w//2, y+h//2
        line = max(w,h) 
        x1, y1 = center_x-line//2-self.offset,  center_y-line//2-self.offset
        x2, y2 = center_x+line//2+self.offset, center_y+line//2+self.offset
        
        # # 범위 초과 확인
        if x1<0 or y1<0 or x2>320 or y2>240: return

        # 손만 떼어오기
        img = frame[y1:y2, x1:x2]

        # BGR을 RGB로 변경
        img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        img = img/255.0
        img = cv2.resize(img, (28,28))

        img = np.expand_dims(img, -1)
        img = np.expand_dims(img, 0)

        self.interpreter.set_tensor(self.input_details[0]['index'], img.astype(self.input_dtype))
        self.interpreter.invoke()
        output_data = self.interpreter.get_tensor(self.output_details[0]['index'])[0]
        self.ans = np.argmax(output_data)
        text = self.ansToText[self.ans]
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
        cv2.putText(frame, text, (x1, y1 - 7), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

    def run(self):
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret: break
            curTime = time.time()
            fps = 1 / (curTime - self.startTime)
            self.startTime = curTime
            self.process_image(frame)
            cv2.putText(frame, f'FPS: {fps:.1f}', (20, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 2)
            cv2.imshow('cam', frame)
            key = cv2.waitKey(10)
            if key == ord('q'): break
        self.cap.release()
        cv2.destroyAllWindows()

    def get_ans(self):
        return self.ans