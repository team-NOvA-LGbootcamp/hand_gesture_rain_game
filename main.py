import threading
import time
import sys
from hand_gesture_recognition import HandGestureRecognition
from rain_game import RainGame
import pygame

def main():
    model_path = 'sample.tflite'
    hgr = HandGestureRecognition(model_path)
    
    # hgr.run()을 별도의 스레드에서 실행
    run_thread = threading.Thread(target=hgr.run)
    run_thread.start()

    game = RainGame()
    buttons = game.draw_start_screen()
    pygame.display.flip()
    try:
        while True:
            ans = hgr.get_ans()
            if ans is not None:
                print(f"Current gesture: {ans}")
            # time.sleep(1)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    for level, button_rect in buttons:
                        if button_rect.collidepoint(mouse_pos):
                            settings = game.DIFFICULTIES[level]
                            game.game_loop(settings['interval'], settings['speed'])
        
            pygame.display.flip()

    except KeyboardInterrupt:
        print("Interrupted by user")
    finally:
        # 스레드가 종료될 때까지 기다림
        run_thread.join()

if __name__ == "__main__":
    main()