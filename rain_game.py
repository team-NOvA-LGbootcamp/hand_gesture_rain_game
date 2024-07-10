import pygame
import random
import sys

class RainGame:
    def __init__(self):
        pygame.init()

        # 화면 크기 설정
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = pygame.display.get_surface().get_size()
        pygame.display.set_caption("Alphabet Rain Game")

        # 색상 정의
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (200, 200, 200)

        # 폰트 설정
        self.title_font = pygame.font.Font(None, 100)
        self.button_font = pygame.font.Font(None, 74)
        self.game_font = pygame.font.Font(None, 74)
        self.input_font = pygame.font.Font(None, 48)

        # 난이도 설정
        self.DIFFICULTIES = {
            'Easy': {'interval': 1000, 'speed': 2},
            'Medium': {'interval': 800, 'speed': 3},
            'Hard': {'interval': 600, 'speed': 4},
            'Hell': {'interval': 400, 'speed': 5}
        }

    class Alphabet:
        def __init__(self, speed, screen_width):
            self.char = chr(random.randint(65, 90))  # 랜덤 알파벳 (A-Z)
            self.x = random.randint(0, screen_width - 50)
            self.y = 0
            self.speed = speed
        
        def draw(self, screen, game_font, color):
            text = game_font.render(self.char, True, color)
            screen.blit(text, (self.x, self.y))
        
        def update(self):
            self.y += self.speed

    def draw_start_screen(self):
        self.screen.fill(self.WHITE)
        title_surface = self.title_font.render("Alphabet Rain", True, self.BLACK)
        self.screen.blit(title_surface, (self.SCREEN_WIDTH // 2 - title_surface.get_width() // 2, 100))
        
        buttons = []
        for i, (level, settings) in enumerate(self.DIFFICULTIES.items()):
            button_rect = pygame.Rect(self.SCREEN_WIDTH // 2 - 100, 250 + i * 100, 200, 50)
            buttons.append((level, button_rect))
            pygame.draw.rect(self.screen, self.GRAY, button_rect)
            text_surface = self.button_font.render(level, True, self.BLACK)
            self.screen.blit(text_surface, (button_rect.x + (button_rect.width - text_surface.get_width()) // 2,
                                       button_rect.y + (button_rect.height - text_surface.get_height()) // 2))
        return buttons

    def game_loop(self, interval, speed):
        alphabets = []
        input_box = pygame.Rect(50, self.SCREEN_HEIGHT - 100, 140, 50)
        user_text = ''
        last_alphabet_time = pygame.time.get_ticks()
        clock = pygame.time.Clock()
        running = True
        while running:
            self.screen.fill(self.WHITE)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if user_text:
                            # 입력창에 입력된 알파벳과 일치하는 가장 아래의 알파벳 제거
                            target_char = user_text.upper()
                            target_alphabet = None
                            for alphabet in alphabets:
                                if alphabet.char == target_char:
                                    if target_alphabet is None or alphabet.y > target_alphabet.y:
                                        target_alphabet = alphabet
                            if target_alphabet:
                                alphabets.remove(target_alphabet)
                            user_text = ''
                    elif event.key == pygame.K_BACKSPACE:
                        user_text = user_text[:-1]
                    else:
                        user_text += event.unicode
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if exit_button_rect.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()


            # 현재 시간 가져오기
            current_time = pygame.time.get_ticks()

            # 일정 시간 간격으로 새 알파벳 생성
            if current_time - last_alphabet_time > interval:
                alphabets.append(self.Alphabet(speed, self.SCREEN_WIDTH))
                last_alphabet_time = current_time

            # 알파벳 업데이트 및 그리기
            for alphabet in alphabets:
                alphabet.update()
                alphabet.draw(self.screen, self.game_font, self.BLACK)

            # 바닥에 닿은 알파벳 제거
            alphabets = [alphabet for alphabet in alphabets if alphabet.y < self.SCREEN_HEIGHT]

            # 입력창 그리기
            pygame.draw.rect(self.screen, self.BLACK, input_box, 2)
            text_surface = self.input_font.render(user_text, True, self.BLACK)
            self.screen.blit(text_surface, (input_box.x + 5, input_box.y + 5))
            input_box.w = max(100, text_surface.get_width() + 10)

            # Add Exit button at the top-right corner
            exit_button_rect = pygame.Rect(self.SCREEN_WIDTH - 70, 20, 50, 50)
#             pygame.draw.rect(self.screen, self.GRAY, exit_button_rect)
            exit_text_surface = self.button_font.render("Exit", True, self.BLACK)
            self.screen.blit(exit_text_surface, (exit_button_rect.x + (exit_button_rect.width - exit_text_surface.get_width()) // 1,
                                              exit_button_rect.y + (exit_button_rect.height - exit_text_surface.get_height()) // 2))

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
