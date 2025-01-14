import pygame
import sys, socket
from pygame import Vector2, Rect, Surface
from pygame.sprite import *

# Инициализация
pygame.init()
host, port = '26.68.85.151', 7891
size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
state, running = "Load", True
screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
screen.fill("black")


# Функции
def but1_func():
    global state
    state = "Play"


def but2_func():
    global running
    running = False


# Классы
class FonUi(Sprite):
    try:
        img = pygame.image.load("data/space.png").convert_alpha()
        r_img = img.get_rect()
    except Exception as e:
        print(str(e))
        sys.exit(-1)

    def __init__(self, group, fon_size, pos=(0, 0)):
        super().__init__(group)
        self.pos = pos
        self.image = pygame.Surface(fon_size)
        self.image.fill("black")
        for i in range(fon_size[1] // FonUi.r_img.size[1] + 2):
            for j in range(fon_size[0] // FonUi.r_img.size[0] + 2):
                rct = FonUi.r_img
                rct.topleft = (j * rct.size[0], i * rct.size[1])
                self.image.blit(FonUi.img, rct)
        self.rect = Rect(*pos, *fon_size)


class TextUi(Sprite):
    def __init__(self, group, text, position=(-1, -1), text_size=(100, 100), font_size=50, color=(255, 255, 255)):
        super().__init__(group)
        self.text = text
        self.color = color
        font = pygame.font.Font(None, font_size)
        self.image = font.render(self.text, True, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = position if position != (-1, -1) else Vector2(*size) // 2
        self.rect.size = text_size


class ButtonUi(Sprite):
    def __init__(self, group, meth, text="", position=(-1, -1), button_size=(200, 100), font_size=50,
                 txt_col=(255, 255, 255), col=(0, 0, 255)):
        super().__init__(group)
        self.image = Surface((200, 100))
        self.rect = self.image.get_rect()
        self.rect.center = position if position != (-1, -1) else Vector2(*size) // 2
        self.rect.size = button_size
        self.image.fill(col)
        self.meth = meth
        self.color = col
        font = pygame.font.Font(None, font_size)
        self.text = font.render(text, True, txt_col)
        self.text_rect = self.text.get_rect()
        self.text_rect.center = Vector2(*self.rect.size) // 2
        self.image.blit(self.text, self.text_rect)

    def update(self, events, *args, **kwargs):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
                self.meth()
            if event.type == pygame.MOUSEMOTION:
                if self.rect.collidepoint(*event.pos):
                    self.image = Surface((200, 100))
                    self.image.fill((0, 0, 200))
                    self.image.blit(self.text, self.text_rect)
                else:
                    self.image = Surface((200, 100))
                    self.image.fill((0, 0, 255))
                    self.image.blit(self.text, self.text_rect)


class Player(Sprite):
    try:
        img = pygame.image.load("data/player.png").convert_alpha()
        img = pygame.transform.scale(img, (100, 100))
    except Exception as e:
        print(e)
        sys.exit(-1)

    def __init__(self, group, nick):
        super().__init__(group)
        self.image = Player.img
        self.nick = nick
        font = pygame.font.Font(None, 50)
        text = font.render(self.nick, True, (255, 255, 255))
        rct = text.get_rect()
        rct.center = (50, 50)
        rct.size = (100, 100)
        self.image.blit(text, rct)
        self.rect = self.image.get_rect()
        self.rect.center = Vector2(*size) // 2
        self.move = Vector2(0, 0)
        self.pos = Vector2(0, 0)
        self.ulta = False

    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.ulta = True
                    self.image = Player.img
                if event.key == pygame.K_d:
                    self.move.x += 10
                if event.key == pygame.K_a:
                    self.move.x -= 10
                if event.key == pygame.K_s:
                    self.move.y += 10
                if event.key == pygame.K_w:
                    self.move.y -= 10
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    self.ulta = False
                    self.image = Player.img
                    font = pygame.font.Font(None, 50)
                    text = font.render(self.nick, True, (255, 255, 255))
                    rct = text.get_rect()
                    rct.center = (50, 50)
                    rct.size = (100, 100)
                    self.image.blit(text, rct)
                if event.key == pygame.K_d:
                    self.move.x -= 10
                if event.key == pygame.K_a:
                    self.move.x += 10
                if event.key == pygame.K_s:
                    self.move.y -= 10
                if event.key == pygame.K_w:
                    self.move.y += 10
        self.rect = self.rect.move(*self.move)
        """if self.ulta and enemy.ulta:
            pass
        elif enemy.ulta:
            move = Vector2(*enemy.rect.center) - Vector2(*self.rect.center)
            if move.length() < 1:
                return
            move = move.normalize() * 10
            move = (round(move.x), round(move.y))
            self.rect = self.rect.move(*move)"""


def main(window_main):
    global state, running
    # Создание экрана
    pygame.display.set_caption(window_main)
    # Создание переменных
    Scenes = {"Load": Group(), "Register": Group(), "Menu": Group(), "Play": Group(), "Finish": Group()}
    is_connect, con_errs = False, 0
    fps = 60
    clock = pygame.time.Clock()
    # Конфигурация сцен
    FonUi(Scenes["Load"], (2000, 2000))
    FonUi(Scenes["Menu"], (2000, 2000))
    FonUi(Scenes["Play"], (10000, 10000))
    TextUi(Scenes["Load"], "Waiting for connection", text_size=(500, 200))
    TextUi(Scenes["Menu"], "BlackHole.io", text_size=(500, 200), position=Vector2(size[0] // 2, 200))
    ButtonUi(Scenes["Menu"], but1_func, "Play", button_size=(200, 100),
             position=Vector2(*size) // 2 + Vector2(0, 200))
    ButtonUi(Scenes["Menu"], but2_func, "Exit", button_size=(200, 100),
             position=Vector2(*size) // 2 + Vector2(0, 300))
    player = Player(Scenes["Play"], "")
    # Основной игровой цикл
    while running:
        events = pygame.event.get()
        if pygame.QUIT in [e.type for e in events]:
            running = False

        if not is_connect:
            # Подключение
            ClientSocket = socket.socket()
            Scenes[state].draw(screen)
            pygame.display.flip()
            try:
                ClientSocket.connect((host, port))
            except socket.error as e:
                print(str(e))
                return -1
            log_en = ClientSocket.recv(2048)
            client_id = int(log_en.decode('utf-8'))
            is_connect, state = True, "Menu"
        else:
            try:
                # Взаимодействие с сервером
                ClientSocket.send(str.encode(f'[{client_id}, {player.rect.center}, {player.ulta}, {player.nick}]'))
                log = eval(ClientSocket.recv(2048).decode('utf-8'))
                con_errs = 0
            except Exception as e:
                con_errs += 1
                if con_errs >= 60:
                    print(str(e))
                    return -1

        Scenes[state].update(events)
        screen.fill("black")
        Scenes[state].draw(screen)
        pygame.display.flip()
        clock.tick(fps)
    pygame.quit()
    ClientSocket.close()
    return 0


if __name__ == '__main__':
    sys.exit(main("Онлайн"))
