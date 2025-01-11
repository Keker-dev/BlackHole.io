import pygame
import sys, socket
from pygame import Vector2, Rect
from pygame.sprite import *

# Инициализация
pygame.init()
host, port = '26.68.85.151', 7891
size = (800, 800)
state = 0
screen = pygame.display.set_mode(size)
screen.fill("black")


# Функции
def but1_func():
    global state
    state = 2


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
    base_image = pygame.Surface((200, 100))

    def __init__(self, group, meth, text="", position=(-1, -1), button_size=(200, 100), font_size=50,
                 txt_col=(255, 255, 255), col=(0, 0, 255)):
        super().__init__(group)
        self.image = ButtonUi.base_image
        self.rect = self.image.get_rect()
        self.rect.center = position if position != (-1, -1) else Vector2(*size) // 2
        self.rect.size = button_size
        self.image.fill(col)
        self.meth = meth
        self.text = text
        self.color = col
        self.text_color = txt_col
        font = pygame.font.Font(None, font_size)
        txt = font.render(self.text, True, self.text_color)
        txt_rect = txt.get_rect()
        txt_rect.center = Vector2(*self.rect.size) // 2
        print(self.rect, txt_rect)
        self.image.blit(txt, txt_rect)

    def update(self, events, *args, **kwargs):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
                self.meth()


class Player(Sprite):
    try:
        img = pygame.image.load("data/player.png").convert_alpha()
        img = pygame.transform.scale(img, (100, 100))
        base = pygame.Surface((100, 100))
        base.fill("blue")
    except Exception as e:
        print(e)
        sys.exit(-1)

    def __init__(self, group, nick):
        super().__init__(group)
        self.image = Player.base
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
                    self.image = Player.base
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
    global state
    # Создание экрана
    pygame.display.set_caption(window_main)
    # Создание переменных
    Scenes = [Group(), Group(), Group()]
    is_connect, con_errs = False, 0
    running, fps = True, 60
    clock = pygame.time.Clock()
    # Конфигурация сцен
    FonUi(Scenes[0], (10000, 10000))
    FonUi(Scenes[1], (10000, 10000))
    FonUi(Scenes[2], (10000, 10000))
    TextUi(Scenes[0], "Waiting for connection", text_size=(500, 200))
    ButtonUi(Scenes[1], but1_func, "Play", button_size=(200, 100))
    player = Player(Scenes[2], "")
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
            is_connect, state = True, 1
        else:
            try:
                # Взаимодействие с сервером
                ClientSocket.send(str.encode(f'[{client_id}, {player.rect.center}, {player.ulta}, {player.nick}]'))
                log_de = eval(ClientSocket.recv(2048).decode('utf-8'))
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
