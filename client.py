import struct
import time
import pygame
import faulthandler
import sys, socket
from pygame import Vector2, Rect, Surface, mixer
from pygame.sprite import *

# Инициализация
pygame.init()
host, port = '26.68.85.151', 7891
size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
state, running, volume = "Load", True, 0.4
screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
screen.fill("black")
try:
    with open("user.dat", "rb") as f:
        user = f.read().decode('utf-8').split('|')
        user = [int(user[0]), user[1], user[2]]
except FileNotFoundError:
    user = None


# Функции
def but_sett():
    global state
    state = "Settings"


def but_menu():
    global state
    state = "Menu"


def but_play_mode(buts):
    for but in buts:
        but.isActive = not but.isActive


def but_reg(login, password):
    global user
    user = [0, login.text, str(hash(password.text))]


def but_play():
    global state
    state = "Game"


def but_exit():
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
        self._text = text
        self.color = color
        self.font = pygame.font.Font(None, font_size)
        self.image = self.font.render(self._text, True, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = position if position != (-1, -1) else Vector2(*size) // 2
        self.rect.size = text_size

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, new_text):
        self._text = new_text
        self.image = self.font.render(self._text, True, self.color)


class ButtonUi(Sprite):
    click_msc = mixer.Channel(1)
    click_msc.set_volume(volume)
    sound = mixer.Sound('data/click_music.mp3')

    def __init__(self, group, meth, text="", position=(-1, -1), button_size=(200, 100), font_size=50,
                 txt_col=(255, 255, 255), meth_args=tuple(), meth_kwargs=dict.fromkeys(tuple(), 0)):
        super().__init__(group)
        if meth_args is None:
            meth_args = []
        self.image = Surface(button_size)
        self.rect = self.image.get_rect()
        self.rect.center = position if position != (-1, -1) else Vector2(*size) // 2
        self.image.fill((0, 0, 255))
        self.meth = meth
        self.params = [meth_args, meth_kwargs]
        self.focus = False
        font = pygame.font.Font(None, font_size)
        self.text = font.render(text, True, txt_col)
        self.text_rect = self.text.get_rect()
        self.text_rect.center = Vector2(*self.rect.size) // 2
        self.image.blit(self.text, self.text_rect)

    def draw_button(self, focus=False, col=(0, 0, 255, 255), click_col=(0, 0, 200, 255)):
        self.image = Surface(self.rect.size)
        self.image.fill(click_col if focus else col)
        self.image.set_alpha(click_col[3] if focus else col[3])
        self.image.blit(self.text, self.text_rect)

    def update(self, events, *args, **kwargs):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
                ButtonUi.click_msc.play(ButtonUi.sound)
                self.meth(*self.params[0], **self.params[1])
            if event.type == pygame.MOUSEMOTION:
                self.focus = self.rect.collidepoint(*event.pos)
                self.draw_button(self.focus)


class AppearButton(ButtonUi):
    def __init__(self, *args, appear_time=1000, **kwargs):
        super().__init__(*args, **kwargs)
        self._isActive = False
        self.startTime = 0
        self.appear_time = appear_time

    def update(self, events, *args, **kwargs):
        if self._isActive:
            t = int((time.time() - self.startTime) * 1000)
            super().update(events, *args, **kwargs)
            alpha = t / self.appear_time
            alpha = int(255 * (1 if alpha > 1 else alpha))
            super().draw_button(self.focus, (0, 0, 255, alpha), (0, 0, 200, alpha))
        else:
            self.image = Surface((0, 0))

    @property
    def isActive(self):
        return self._isActive

    @isActive.setter
    def isActive(self, val):
        self._isActive = val
        if self._isActive:
            self.startTime = time.time()
        else:
            self.startTime = 0


class SliderUI(Sprite):
    def __init__(self, group, num=0, position=(-1, -1), sl_size=(300, 100), point_size=(75, 100), font_size=50):
        super().__init__(group)
        self.rect = Rect(*position, *sl_size)
        self.rect.center = position if position != (-1, -1) else Vector2(*size) // 2
        self.num = num
        self.focus = False
        self.point_size = point_size
        self.work_surf = (self.rect.size[0] - self.point_size[0]) / 100
        self.font = pygame.font.Font(None, font_size)
        self.draw_UI()

    def draw_UI(self):
        self.image = Surface(self.rect.size)
        self.image.fill((100, 100, 100))
        back = Surface((self.rect.size[0] // 100 * self.num if self.num else 0, self.rect.size[1]))
        back.fill((255, 255, 255))
        point = Surface(self.point_size)
        point.fill((0, 0, 200) if self.focus else (0, 0, 255))
        p_rect = point.get_rect()
        p_rect.midleft = (self.num * self.work_surf if self.num else 0, self.rect.size[1] // 2)
        txt = self.font.render(str(self.num), True, (255, 255, 255))
        txt_rect = txt.get_rect()
        txt_rect.center = Vector2(*p_rect.size) // 2
        point.blit(txt, txt_rect)
        self.image.blit(back, (0, 0))
        self.image.blit(point, p_rect)

    def update(self, events, *args, **kwargs):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
                ButtonUi.click_msc.play(ButtonUi.sound)
                self.num = round((event.pos[0] - self.rect.left - self.point_size[0] // 2) / self.work_surf)
                self.num = self.num if self.num >= 0 else 0
                self.num = self.num if self.num <= 100 else 100
                self.focus = True
                self.draw_UI()
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.focus = False
                self.draw_UI()
            elif self.focus and event.type == pygame.MOUSEMOTION:
                self.num = round((event.pos[0] - self.rect.left - self.point_size[0] // 2) / self.work_surf)
                self.num = self.num if self.num >= 0 else 0
                self.num = self.num if self.num <= 100 else 100
                self.draw_UI()


class InputUI(Sprite):
    def __init__(self, group, position=(-1, -1), input_size=(200, 100), font_size=50, max_syms=50):
        super().__init__(group)
        self.image = Surface(input_size)
        self.rect = self.image.get_rect()
        self.rect.center = position if position != (-1, -1) else Vector2(*size) // 2
        self.font = pygame.font.Font(None, font_size)
        self.max_syms = max_syms
        self.Active = False
        self.text = ""
        self.drawUI()

    def update(self, events, *args, **kwargs):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.Active = self.rect.collidepoint(event.pos)
                self.drawUI()
            if event.type == pygame.KEYDOWN and self.Active:
                if event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
                    self.text = self.text[:-1]
                elif event.key == pygame.K_RETURN:
                    self.Active = False
                elif len(self.text) < self.max_syms:
                    self.text += event.unicode
                self.drawUI()

    def drawUI(self):
        self.image = Surface(self.rect.size)
        self.image.fill((255, 255, 255))
        if not self.Active:
            self.image.fill((0, 0, 0), Rect(2, 2, self.rect.size[0] - 4, self.rect.size[1] - 4))
        else:
            self.image.fill((50, 50, 50), Rect(2, 2, self.rect.size[0] - 4, self.rect.size[1] - 4))
        text_image = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_image.get_rect()
        text_rect.center = Vector2(*self.rect.size) // 2
        if text_rect.size[0] > self.rect.size[0] - 12:
            text_rect.left = self.rect.size[0] - 12 - text_rect.size[0]
        else:
            text_rect.left = 6
        self.image.blit(text_image, text_rect)


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

    def set_nick(self, new_nick):
        self.nick = new_nick
        self.image = Player.img
        font = pygame.font.Font(None, 50)
        text = font.render(self.nick, True, (255, 255, 255))
        rct = text.get_rect()
        rct.center = (50, 50)
        rct.size = (100, 100)
        self.image.blit(text, rct)

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
    global state, running, user, volume
    # Создание экрана
    pygame.display.set_caption(window_main)
    # Создание переменных
    fon_msc = mixer.Channel(0)
    fon_msc.set_volume(volume)
    fon_msc.play(mixer.Sound('data/fon_music.mp3'), fade_ms=1000, loops=-1)
    ClientSocket, client_id = None, None
    Scenes = {"Load": Group(), "Register": Group(), "Menu": Group(), "Game": Group(), "Finish": Group(),
              "Settings": Group()}
    con_errs, is_reg = 0, False
    fps = 60
    clock = pygame.time.Clock()
    # Конфигурация сцен
    FonUi(Scenes["Load"], (2000, 2000))
    FonUi(Scenes["Register"], (2000, 2000))
    FonUi(Scenes["Menu"], (2000, 2000))
    FonUi(Scenes["Settings"], (2000, 2000))
    FonUi(Scenes["Game"], (22000, 22000))
    TextUi(Scenes["Load"], "Waiting for connection", text_size=(500, 200))
    TextUi(Scenes["Register"], "Вход/Регистрация", text_size=(500, 200), position=Vector2(size[0] // 2, 200))
    TextUi(Scenes["Register"], "Логин:", position=Vector2(size[0] // 2, size[1] // 2 - 100))
    TextUi(Scenes["Register"], "Пароль:", position=Vector2(*size) // 2 + Vector2(0, 50))
    TextUi(Scenes["Menu"], "BlackHole.io", text_size=(500, 200),
           position=Vector2(size[0] // 2, 200), font_size=100)
    TextUi(Scenes["Settings"], "Громкость:", text_size=(300, 100), position=Vector2(*size) // 2 + Vector2(0, -100))
    loginUI = InputUI(Scenes["Register"], input_size=(400, 100), position=Vector2(*size) // 2 + Vector2(0, -25))
    passwordUI = InputUI(Scenes["Register"], position=Vector2(*size) // 2 + Vector2(0, 125), input_size=(400, 100))
    ButtonUi(Scenes["Register"], but_reg, "Вход", button_size=(200, 100),
             position=Vector2(size[0] // 2, size[1] - 200), meth_args=(loginUI, passwordUI))
    def_mode = AppearButton(Scenes["Menu"], but_play, "Доп. режим", button_size=(300, 100),
                            position=Vector2(size[0] // 2 + 400, size[1] - 350))
    dop_mode = AppearButton(Scenes["Menu"], but_play, "Обычный режим", button_size=(300, 100),
                            position=Vector2(size[0] // 2 + 400, size[1] - 450))
    edu_mode = AppearButton(Scenes["Menu"], but_play, "Обучение", button_size=(300, 100),
                            position=Vector2(size[0] // 2 - 400, size[1] - 350))
    bot_mode = AppearButton(Scenes["Menu"], but_play, "Игра с ботами", button_size=(300, 100),
                            position=Vector2(size[0] // 2 - 400, size[1] - 250))
    ButtonUi(Scenes["Menu"], but_play_mode, "Мультиплеер", button_size=(300, 100),
             position=Vector2(size[0] // 2, size[1] - 400), meth_args=([def_mode, dop_mode],))
    ButtonUi(Scenes["Menu"], but_play_mode, "Синглплеер", button_size=(300, 100),
             position=Vector2(size[0] // 2, size[1] - 300), meth_args=([edu_mode, bot_mode],))
    ButtonUi(Scenes["Menu"], but_sett, "Настройки", button_size=(300, 100),
             position=Vector2(size[0] // 2, size[1] - 200))
    ButtonUi(Scenes["Menu"], but_exit, "Выход", button_size=(300, 100),
             position=Vector2(size[0] // 2, size[1] - 100))
    ButtonUi(Scenes["Settings"], but_menu, "Меню", button_size=(100, 100), position=Vector2(50, 50))
    vloume_sl = SliderUI(Scenes["Settings"], 50, sl_size=(300, 100))
    player = Player(Scenes["Game"], user[1] if user else "")
    # Подключение
    ClientSocket = socket.socket()
    Scenes["Load"].draw(screen)
    pygame.display.flip()
    try:
        ClientSocket.connect((host, port))
    except socket.error as error:
        print(str(error))
        return -1
    if not user:
        state = "Register"
    # Основной игровой цикл
    while running:
        events = pygame.event.get()
        if pygame.QUIT in [i.type for i in events]:
            running = False

        if not is_reg and user:
            ClientSocket.send(str.encode(f'reg {[user[1], user[2]]}'))
            log = ClientSocket.recv(2048).decode('utf-8').split(" ", maxsplit=2)
            if log[0] == "reg" and log[1] == "True":
                state = "Menu"
                user[0] = int(log[2])
                with open("user.dat", "wb") as f:
                    f.write(str.encode("|".join(map(str, user))))
                player.set_nick(user[1])
                is_reg = True
            else:
                state = "Register"
                user = None
        if state == "Settings":
            volume = 0.8 * (vloume_sl.num / 100)
            fon_msc.set_volume(volume)
            ButtonUi.click_msc.set_volume(volume)
        if state == "Game":
            try:
                # Взаимодействие с сервером
                ClientSocket.send(str.encode(f'[{client_id}, {player.rect.center}, {player.ulta}, {player.nick}]'))
                log = eval(ClientSocket.recv(2048).decode('utf-8'))
                con_errs = 0
            except Exception as error:
                con_errs += 1
                if con_errs >= 60:
                    print(str(error))
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
    faulthandler.enable()
    sys.exit(main("BlackHole.io"))
