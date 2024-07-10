import threading
import time
from hand_gesture_recognition import HandGestureRecognition

def main():
    model_path = 'sample.tflite'
    hgr = HandGestureRecognition(model_path)
    
    # hgr.run()을 별도의 스레드에서 실행
    run_thread = threading.Thread(target=hgr.run)
    run_thread.start()
    
    try:
        while True:
            ans = hgr.get_ans()
            if ans is not None:
                print(f"Current gesture: {ans}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Interrupted by user")
    finally:
        # 스레드가 종료될 때까지 기다림
        run_thread.join()

if __name__ == "__main__":
    main()