import threading
import time
import sys

from rain_game import RainGame
import pygame

MODEL = True
stop_event = threading.Event()

if MODEL:
    print("Loading model")
    from hand_gesture_recognition import HandGestureRecognition
    print("Model is Ready")

def run_game(game):
    while not stop_event.is_set():
        if game.get_game_starter():
            game.game_loop(stop_event)
        else:
            game.game_ready()
    

def main():
    if MODEL:
        model_path = 'SignMNIST_RainGame.tflite'
        hgr = HandGestureRecognition(model_path)
        
        # hgr.run()을 별도의 스레드에서 실행
        hgr_thread = threading.Thread(target=hgr.run, args=(stop_event,), daemon=True)
        hgr_thread.start()
    
    game = RainGame()
    pygame.display.flip()
    
    # RainGame을 별도의 스레드에서 실행
    game_thread = threading.Thread(target=run_game, args=(game,), daemon=True)
    game_thread.start()
    
    try:
        while not stop_event.is_set():
            if MODEL:
                ans = hgr.get_ans()
                game.set_cam_input(ans)
                game.set_cam_frame(hgr.get_frame())
                time.sleep(0.1)  # CPU 사용량을 줄이기 위해 잠시 대기
            
    except KeyboardInterrupt:
        print("Interrupted by user")
        stop_event.set()
    finally:
        # 스레드가 종료될 때까지 기다림
        hgr_thread.join()
        game_thread.join()

if __name__ == "__main__":
    main()