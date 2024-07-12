import pygame
import random
import sys
import cv2
from pygame.locals import *
from pygame import mixer


game_margin = 8
class RainGame:
    def __init__(self):
        pygame.init()

        # 화면 크기 설정
        self.SCREEN_WIDTH = 1000
        self.SCREEN_HEIGHT = 500
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Alphabet Rain Game")
        self.camera_frame = []
        
        # 색상 정의
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (200, 200, 200)

        # 색상 정의
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (200, 200, 200)
        self.PRETTY_BLUE = (100,149,237)

        # 폰트 설정
        self.title_font = pygame.font.Font(None, 100)
        self.button_font = pygame.font.Font(None, 74)
        self.game_font = pygame.font.Font(None, 74)
        self.input_font = pygame.font.Font(None, 48)

        # 알파벳 영역 설정 (화면 세로방향 약 3/4 지점)
        self.remove_zone_top = self.SCREEN_HEIGHT * 3 // 4 - 100
        self.remove_zone_bottom = self.SCREEN_HEIGHT * 3 // 4 + 0
        # 알파벳 이미지 로드
        self.images = {
            'A': pygame.image.load('./icons/icon_A.png'),
            'B': pygame.image.load('./icons/icon_B.png'),
            'F': pygame.image.load('./icons/icon_F.png'),
            'V': pygame.image.load('./icons/icon_V.png'),
            'Y': pygame.image.load('./icons/icon_Y.png')
        }

        # 알파벳 고정 위치 설정
        fixed=10
        self.alphabet_positions = {
            'A': 20,
            'B': self.SCREEN_WIDTH // game_margin * 1 - fixed,
            'F': self.SCREEN_WIDTH // game_margin * 2 - fixed,
            'V': self.SCREEN_WIDTH // game_margin * 3 - fixed,
            'Y': self.SCREEN_WIDTH // game_margin * 4 - fixed,
        }

        # 알파벳 등장 간격 리스트 및 인덱스
        # self.intervals = [3500+1700]+[1700]*10 # ms
        self.intervals = [1000]+[1700]*50 # ms
        self.interval_index = 0
        self.speed = 1
        self.score = 0

        # 게임 상태 관련 변수
        self.game_over = False
        self.game_starter = False

        # 노래 설정
        mixer.init()
        self.background_music = mixer.Sound('nabi.wav')
        
        # Cam전달 변수
        self.cam_input = -1
        self.start_button_rect = self.draw_start_screen()

        #frame
        self.frame = None

    class Alphabet:
        def __init__(self, char, x_position, speed, image):
            self.char = char
            self.x = x_position
            self.y = 0
            self.speed = speed
            self.image = image
        
        def draw(self, screen, game_font=None):
            screen.blit(self.image, (self.x, self.y))
        
        def update(self):
            self.y += self.speed

    def set_cam_input(self, ans):
        self.cam_input = ans

    def set_cam_frame(self, frame):
        self.frame = frame

    
    def get_game_starter(self):
        return self.game_starter

    def draw_start_screen(self):
        self.screen.fill(self.WHITE)
        title_surface = self.title_font.render("Rhythm Alphabet Game", True, self.BLACK)
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

    def game_ready(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if self.start_button_rect.collidepoint(mouse_pos):
                    self.score = 0
                    self.interval_index = 0
                    self.play_background_music()
                    self.game_starter = True

    def game_loop(self):
        alphabets = []
        last_alphabet_time = pygame.time.get_ticks()
        clock = pygame.time.Clock()
        pygame.display.flip()  

        while True:
            if not self.game_over:
                self.screen.fill(self.WHITE)
                pygame.draw.rect(self.screen, (150, 220, 150), (0, (self.remove_zone_top+self.remove_zone_bottom)/2, self.SCREEN_WIDTH - 240, 100))
                
                if self.cam_input != -1:
                    chars = 'ABFVY'
                    target_char = chars[self.cam_input]
                    image = self.images[target_char]
                    x_t = self.alphabet_positions[target_char]-10
                    y_t = 0
                    pygame.draw.rect(self.screen, (220, 150, 150), (x_t,y_t,65,500))
                

                    target_alphabet = None

                    for alphabet in alphabets:
                        if alphabet.char == target_char and self.remove_zone_top < alphabet.y < self.remove_zone_bottom:
                            target_alphabet = alphabet
                            break
                    if target_alphabet:
                        alphabets.remove(target_alphabet)
                        self.score += 1

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                # 현재 시간 가져오기
                current_time = pygame.time.get_ticks()

                # 일정 시간 간격으로 새 알파벳 생성
                if current_time - last_alphabet_time > self.intervals[self.interval_index]:
                    char = random.choice('ABFVY')
                    image = self.images[char]
                    alphabets.append(self.Alphabet(char, self.alphabet_positions[char], self.speed, image))
                    last_alphabet_time = current_time
                    self.interval_index = (self.interval_index + 1) % len(self.intervals)

                    # interval loop가 끝나면 game_over를 True로 설정
                    if self.interval_index == len(self.intervals) - 1:
                        self.game_over = True

                # 알파벳 업데이트 및 그리기
                for alphabet in alphabets:
                    alphabet.update()
                    alphabet.draw(self.screen, self.game_font)

                # 바닥에 닿은 알파벳 제거 및 감점
                for alphabet in alphabets[:]:
                    if alphabet.y > self.SCREEN_HEIGHT-10:
                        alphabets.remove(alphabet)
                        if self.score > 0:
                            self.score -= 1


                # 고정된 알파벳 그리기
                fixed=10
                self.screen.blit(self.images['A'], (20, self.SCREEN_HEIGHT - 60))
                self.screen.blit(self.images['B'], (self.SCREEN_WIDTH // game_margin * 1- fixed, self.SCREEN_HEIGHT - 60))
                self.screen.blit(self.images['F'], (self.SCREEN_WIDTH // game_margin * 2 - fixed, self.SCREEN_HEIGHT - 60))
                self.screen.blit(self.images['V'], (self.SCREEN_WIDTH // game_margin * 3 - fixed, self.SCREEN_HEIGHT - 60))
                self.screen.blit(self.images['Y'], (self.SCREEN_WIDTH // game_margin * 4 - fixed, self.SCREEN_HEIGHT - 60))
                # self.screen.blit(text_surface, 
                #                  (self.SCREEN_WIDTH // 2 - text_surface.get_width() // 2, self.SCREEN_HEIGHT - 50))

                # 점수 표시
                score_surface = self.game_font.render(f"Score: {self.score}", True, self.BLACK)
                self.screen.blit(score_surface, (self.SCREEN_WIDTH - 200, self.SCREEN_HEIGHT // 2 - 25))
                
                # 게임 종료 시 처리
                if self.game_over:
                    self.screen.fill(self.WHITE)  # 화면을 검은색으로 지우기
                    retry_text_surface = self.button_font.render("Retry", True, self.BLACK)
                    self.screen.blit(retry_text_surface, (self.SCREEN_WIDTH // 2 - retry_text_surface.get_width() // 2, 260))
                    final_score_surface = self.game_font.render(f"Final Score: {self.score}", True, self.BLACK)
                    self.screen.blit(final_score_surface, (self.SCREEN_WIDTH // 2 - final_score_surface.get_width() // 2, 150))
                    self.stop_background_music()

                if self.frame is not None:
                    frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
                    frame = cv2.resize(frame, (180, 240))  # 웹캠 프레임 크기 조정
                    frame_surface = pygame.surfarray.make_surface(frame)
                    self.screen.blit(frame_surface, (self.SCREEN_WIDTH - 240, 30))  # 오른쪽 위에 웹캠 프레임 그리기
                
                pygame.display.flip()
                clock.tick(30)

            else:
                self.screen.fill(self.WHITE)  # 화면을 흰색으로 지우기
                retry_text_surface = self.button_font.render("Retry", True, self.BLACK)
                self.retry_button_rect = pygame.Rect(self.SCREEN_WIDTH // 2 - 100, 260, 200, 50)
                pygame.draw.rect(self.screen, self.GRAY, self.retry_button_rect)
                self.screen.blit(retry_text_surface, (self.retry_button_rect.x + (self.retry_button_rect.width - retry_text_surface.get_width()) // 2,
                                                     self.retry_button_rect.y + (self.retry_button_rect.height - retry_text_surface.get_height()) // 2))
                final_score_surface = self.game_font.render(f"Final Score: {self.score}", True, self.BLACK)
                self.screen.blit(final_score_surface, (self.SCREEN_WIDTH // 2 - final_score_surface.get_width() // 2, 150))
                self.stop_background_music()
                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = event.pos
                        if self.retry_button_rect and self.retry_button_rect.collidepoint(mouse_pos):
                            self.game_over = False
                            self.game_starter = False
                            alphabets = []
                            self.score = 0
                            self.interval_index = 0
                            self.play_background_music()  # 배경 음악 재생
                            last_alphabet_time = pygame.time.get_ticks()


if __name__ == "__main__":
    main()
