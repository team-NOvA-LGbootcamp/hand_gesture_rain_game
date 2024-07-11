import pygame
import random
import sys
import cv2
from pydub import AudioSegment

class RainGame:
    def __init__(self):
        pygame.init()

        # 화면 크기 설정
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 400
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Alphabet Rain Game")
        self.camera_frame = []
        # 색상 정의
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (200, 200, 200)

        # 폰트 설정
        self.title_font = pygame.font.Font(None, 100)
        self.button_font = pygame.font.Font(None, 74)
        self.game_font = pygame.font.Font(None, 74)
        self.input_font = pygame.font.Font(None, 48)

        # 알파벳 영역 설정 (화면 세로방향 약 3/4 지점)
        self.remove_zone_top = self.SCREEN_HEIGHT * 3 // 4 - 25
        self.remove_zone_bottom = self.SCREEN_HEIGHT * 3 // 4 + 25

        # 알파벳 고정 위치 설정
        self.alphabet_positions = {
            'A': self.SCREEN_WIDTH // 6 * 1 - 20,
            'B': self.SCREEN_WIDTH // 6 * 2 - 20,
            'C': self.SCREEN_WIDTH // 6 * 3 - 20,
            'D': self.SCREEN_WIDTH // 6 * 4 - 20,
            'E': self.SCREEN_WIDTH // 6 * 5 - 20,
        }
        self.interval = 1500
        self.speed = 2

        #audio_init
        audio_file_path = "nabi.wav"
        pygame.mixer.init()
        pygame.mixer.music.load(audio_file_path)
        
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
        title_surface = self.title_font.render("Rhythm Alphabet Game", True, self.BLACK)
        self.screen.blit(title_surface, (self.SCREEN_WIDTH // 2 - title_surface.get_width() // 2, 100))
        
        # Start 버튼
        start_button_rect = pygame.Rect(self.SCREEN_WIDTH // 2 - 100, 250, 200, 50)
        pygame.draw.rect(self.screen, self.GRAY, start_button_rect)
        text_surface = self.button_font.render("Start", True, self.BLACK)
        self.screen.blit(text_surface, (start_button_rect.x + (start_button_rect.width - text_surface.get_width()) // 2,
                                        start_button_rect.y + (start_button_rect.height - text_surface.get_height()) // 2))
        return start_button_rect

    def game_loop(self,):
        alphabets = []
        last_alphabet_time = pygame.time.get_ticks()
        clock = pygame.time.Clock()
        running = True

        pygame.mixer.music.play(-1)  # 반복 재생

        while running:
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

            # 현재 시간 가져오기
            current_time = pygame.time.get_ticks()

            # 일정 시간 간격으로 새 알파벳 생성
            if current_time - last_alphabet_time > self.interval:
                char = random.choice('ABCDE')
                alphabets.append(self.Alphabet(char, self.alphabet_positions[char], self.speed))
                last_alphabet_time = current_time

            # 알파벳 업데이트 및 그리기
            for alphabet in alphabets:
                alphabet.update()
                alphabet.draw(self.screen, self.game_font, self.BLACK)

            # 바닥에 닿은 알파벳 제거
            alphabets = [alphabet for alphabet in alphabets if alphabet.y < self.SCREEN_HEIGHT]

            # 사라질 수 있는 영역 그리기
            pygame.draw.line(self.screen, self.BLACK, (0, self.remove_zone_top), (self.SCREEN_WIDTH, self.remove_zone_top), 2)
            pygame.draw.line(self.screen, self.BLACK, (0, self.remove_zone_bottom), (self.SCREEN_WIDTH, self.remove_zone_bottom), 2)

            # 고정된 알파벳 그리기
            fixed_alphabets = 'A       B       C       D       E'
            text_surface = self.input_font.render(fixed_alphabets, True, self.BLACK)
            self.screen.blit(text_surface, (self.SCREEN_WIDTH // 2 - text_surface.get_width() // 2, self.SCREEN_HEIGHT - 50))

            pygame.display.flip()
            clock.tick(30)

def main():
    game = RainGame()
    buttons = game.draw_start_screen()
    pygame.display.flip()
    
    while True:
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

if __name__ == "__main__":
    main()
