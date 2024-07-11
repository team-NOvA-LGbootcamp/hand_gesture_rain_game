import threading
import time
import sys
from hand_gesture_recognition import HandGestureRecognition
from rain_game import RainGame
import pygame

def main():
    model_path = 'SignMNIST_RainGame.tflite'
    hgr = HandGestureRecognition(model_path)
    
    # hgr.run()을 별도의 스레드에서 실행
    run_thread = threading.Thread(target=hgr.run)
    run_thread.start()

    game = RainGame()
    start_button_rect = game.draw_start_screen()
    pygame.display.flip()
    try:
        while True:
            ans = hgr.get_ans()
            if ans is not None:
                print(f"Current gesture: {ans}")
            time.sleep(1)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if start_button_rect.collidepoint(mouse_pos):
                        game.game_over = False
                        game.score = 0
                        game.interval_index = 0
                        game.play_background_music()
                        game.game_loop()  # 게임 루프 시작

        
            pygame.display.flip()

    except KeyboardInterrupt:
        print("Interrupted by user")
    finally:
        # 스레드가 종료될 때까지 기다림
        run_thread.join()

if __name__ == "__main__":
    main()