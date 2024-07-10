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
        self.ansToText = {0: 'scissors', 1: 'rock', 2: 'paper'}
        self.colorList = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        self.IMG_SIZE = 64
        self.offset = 30
        self.cap = cv2.VideoCapture(camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.startTime = 0
        self.ans = None

    def make_square_img(self, img):
        ho, wo = img.shape[0], img.shape[1]
        aspectRatio = ho / wo
        wbg = np.ones((self.IMG_SIZE, self.IMG_SIZE, 3), np.uint8) * 255
        if aspectRatio > 1:  # portrait
            k = self.IMG_SIZE / ho
            wk = int(wo * k)
            img = cv2.resize(img, (wk, self.IMG_SIZE))
            img_h, img_w = img.shape[0], img.shape[1]
            d = (self.IMG_SIZE - img_w) // 2
            wbg[:img_h, d:img_w + d] = img
        else:  # landscape
            k = self.IMG_SIZE / wo
            hk = int(ho * k)
            img = cv2.resize(img, (self.IMG_SIZE, hk))
            img_h, img_w = img.shape[0], img.shape[1]
            d = (self.IMG_SIZE - img_h) // 2
            wbg[d:img_h + d, :img_w] = img
        return wbg

    def process_image(self, frame):
        hands, _ = self.hd.findHands(frame, draw=False)
        if not hands: return

        x, y, w, h = hands[0]['bbox']
        if x < self.offset or y < self.offset or x + w + self.offset > 640 or y + h > 480: return
        x1, y1 = x - self.offset, y - self.offset
        x2, y2 = x + w + self.offset, y + h
        img = frame[y1:y2, x1:x2]
        img = self.make_square_img(img)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = np.expand_dims(img, 0)
        self.interpreter.set_tensor(self.input_details[0]['index'], img.astype(self.input_dtype))
        self.interpreter.invoke()
        output_data = self.interpreter.get_tensor(self.output_details[0]['index'])[0]
        self.ans = np.argmax(output_data)
        text = self.ansToText[self.ans]
        cv2.rectangle(frame, (x1, y1), (x2, y2), self.colorList[self.ans], 2)
        cv2.putText(frame, text, (x1, y1 - 7), cv2.FONT_HERSHEY_PLAIN, 2, self.colorList[self.ans], 2)

    def run(self):
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret: break
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