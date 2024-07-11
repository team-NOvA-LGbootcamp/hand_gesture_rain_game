import pygame
import random
import sys
import cv2
import numpy as np
# from pydub import AudioSegment
from pygame.locals import *
from pygame import mixer


class RainGame:
    def __init__(self):
        pygame.init()

        # 화면 크기 설정
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Arrow Rhythm Game")
        self.camera_frame = []
        
        # 색상 정의
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (200, 200, 200)
        self.PRETTY_BLUE = (100,149,237)

        # 폰트 설정
        self.title_font = pygame.font.Font(None, 90)
        self.button_font = pygame.font.Font(None, 70)
        self.game_font = pygame.font.Font(None, 60)

        # 알파벳 영역 설정 (화면 세로방향 약 3/4 지점)
        self.remove_zone_top = self.SCREEN_HEIGHT * 3 // 4 - 25
        self.remove_zone_bottom = self.SCREEN_HEIGHT * 3 // 4 + 25

        # 알파벳 고정 위치 설정
        margin_ = 8
        self.alphabet_positions = {
            'A': self.SCREEN_WIDTH // margin_ * 1 - 20,
            'B': self.SCREEN_WIDTH // margin_ * 2 - 20,
            'C': self.SCREEN_WIDTH // margin_ * 3 - 20,
            'D': self.SCREEN_WIDTH // margin_ * 4 - 20,
            'E': self.SCREEN_WIDTH // margin_ * 5 - 20,
        }

        # 알파벳 등장 간격 리스트 및 인덱스
        # self.intervals = [3500+1700]+[1700]*10 # ms
        self.intervals = [100]+[1700]*1000 # ms
        self.interval_index = 0
        self.speed = 3
        self.score = 0

        # 게임 상태 관련 변수
        self.game_over = False

        # 노래 설정
        mixer.init()
        self.background_music = mixer.Sound('nabi.wav')

        # OpenCV 카메라 설정
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)


    class Alphabet:
        def __init__(self, char, x_position, speed):
            self.char = char
            self.x = x_position
            self.y = 0
            self.speed = speed
        
        def draw(self, screen, game_font, color):
            text = game_font.render(self.char, True, color)
            screen.blit(text, (self.x, self.y))
        
        def update(self):
            self.y += self.speed

    def draw_start_screen(self):
        self.screen.fill(self.WHITE)
        title_surface = self.title_font.render("Arrow Rhythm Game", True, self.BLACK)
        self.screen.blit(title_surface, (self.SCREEN_WIDTH // 2 - title_surface.get_width() // 2, 100))
        
        # Start 버튼
        start_button_rect = pygame.Rect(self.SCREEN_WIDTH // 2 - 100, 250, 200, 50)
        pygame.draw.rect(self.screen, self.GRAY, start_button_rect)
        text_surface = self.button_font.render("Start", True, self.BLACK)
        self.screen.blit(text_surface, (start_button_rect.x + (start_button_rect.width - text_surface.get_width()) // 2,
                                        start_button_rect.y + (start_button_rect.height - text_surface.get_height()) // 2))
        return start_button_rect
    
    def play_background_music(self):
        self.background_music.play()  # 노래를 반복 재생
        
    def stop_background_music(self):
        self.background_music.stop()  # 노래를 종료

    def game_loop(self):
        alphabets = []
        last_alphabet_time = pygame.time.get_ticks()
        clock = pygame.time.Clock()

        game_surface = pygame.Surface((self.SCREEN_WIDTH - 200, self.SCREEN_HEIGHT))
        camera_surface = pygame.Surface((320, 240))
        score_surface = pygame.Surface((200, self.SCREEN_HEIGHT))
        
        while not self.game_over:
            self.screen.fill(self.WHITE)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.unicode.lower() in 'abcde':
                        target_char = event.unicode.upper()
                        target_alphabet = None
                        for alphabet in alphabets:
                            if alphabet.char == target_char and self.remove_zone_top < alphabet.y < self.remove_zone_bottom:
                                target_alphabet = alphabet
                                break
                        if target_alphabet:
                            alphabets.remove(target_alphabet)
                            self.score += 1

            # 현재 시간 가져오기
            current_time = pygame.time.get_ticks()

            # 일정 시간 간격으로 새 알파벳 생성
            if current_time - last_alphabet_time > self.intervals[self.interval_index]:
                char = random.choice('ABCDE')
                alphabets.append(self.Alphabet(char, self.alphabet_positions[char], self.speed))
                last_alphabet_time = current_time
                self.interval_index = (self.interval_index + 1) % len(self.intervals)

                # interval loop가 끝나면 game_over를 True로 설정
                if self.interval_index == len(self.intervals) - 1:
                    self.game_over = True

            # 알파벳 업데이트 및 그리기
            game_surface.fill(self.WHITE)
            for alphabet in alphabets:
                alphabet.update()
                alphabet.draw(game_surface, self.game_font, self.PRETTY_BLUE)

            # 바닥에 닿은 알파벳 제거 및 감점
            for alphabet in alphabets[:]:
                if alphabet.y > self.SCREEN_HEIGHT:
                    alphabets.remove(alphabet)
                    self.score -= 1

            # 사라질 수 있는 영역 그리기
            pygame.draw.line(game_surface, self.BLACK, (0, self.remove_zone_top), (self.SCREEN_WIDTH-200, self.remove_zone_top), 2)
            pygame.draw.line(game_surface, self.BLACK, (0, self.remove_zone_bottom), (self.SCREEN_WIDTH-200, self.remove_zone_bottom), 2)

            # 고정된 알파벳 그리기
            blank = " "*8
            fixed_alphabets = f"←{blank}↓{blank}↑{blank}→{blank}*"
            text_surface = self.game_font.render(fixed_alphabets, True, self.BLACK)
            game_surface.blit(text_surface, ((self.SCREEN_WIDTH-200) // 2 - text_surface.get_width() // 2, self.SCREEN_HEIGHT - 50))

            # 점수 표시
            score_surface.fill(self.WHITE)
            score_text = self.game_font.render(f"Score: {self.score}", True, self.BLACK)
            score_surface.blit(score_text, (1, 0))

            # Draw surfaces onto main screen
            self.screen.blit(game_surface, (0, 0))
            self.screen.blit(score_surface, (self.SCREEN_WIDTH - score_surface.get_width() - 20, 20))


            # 카메라 화면 가져오기
            camera_width = 320
            camera_height = 240
            margin_px = 30
            
            ret, frame = self.camera.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # BGR에서 RGB로 변환
                frame = np.rot90(frame)  # 90도 회전
                frame = pygame.surfarray.make_surface(frame)
                frame = pygame.transform.scale(frame, (camera_width, camera_height))
                camera_surface.blit(frame, (0, 0))
                self.screen.blit(camera_surface, (self.SCREEN_WIDTH - 200, 50))
                # score_surface.blit(frame, (self.SCREEN_WIDTH - 200 - camera_width - margin_px, self.SCREEN_HEIGHT - 50 -camera_height - margin_px))

            # 게임 종료 시 처리
            if self.game_over:
                self.screen.fill(self.WHITE)  # 화면을 검은색으로 지우기
                retry_text_surface = self.button_font.render("Retry", True, self.BLACK)
                self.screen.blit(retry_text_surface, (self.SCREEN_WIDTH // 2 - retry_text_surface.get_width() // 2, 260))
                final_score_surface = self.game_font.render(f"Final Score: {self.score}", True, self.BLACK)
                self.screen.blit(final_score_surface, (self.SCREEN_WIDTH // 2 - final_score_surface.get_width() // 2, 150))
                self.stop_background_music()
                
            pygame.display.flip()
            clock.tick(30) #


if __name__ == "__main__":
    main()
