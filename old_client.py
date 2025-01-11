import pygame
import sys
import socket
from pygame import Vector2, Rect
from pygame.sprite import *

pygame.init()
size = (800, 800)
screen = pygame.display.set_mode(size)
screen.fill("black")
pygame.display.set_caption("Онлайн")

Scene = Group()

ClientSocket = socket.socket()
host, port = '26.68.85.151', 7891
print('Waiting for connection')
try:
    ClientSocket.connect((host, port))
except socket.error as e:
    print(str(e))

log_en = ClientSocket.recv(2048)
client_id = int(log_en.decode('utf-8'))
print(f'Ваш ID в игре: {client_id}')


class Enemy(Sprite):
    try:
        img = pygame.image.load("data/player.png").convert_alpha()
        img = pygame.transform.scale(img, (100, 100))
        base = pygame.Surface((100, 100))
        base.fill("red")
    except Exception as e:
        print(e)
        sys.exit(-1)

    def __init__(self, group, nicknam):
        super().__init__(group)
        self.image = pygame.Surface((100, 100))
        self.image.fill("red")
        self.rect = self.image.get_rect()
        self.rect.center = Vector2(*size) // 2
        self.ulta = False
        self.nick = nicknam
        self.id = -999

    def is_ulta(self):
        if self.ulta:
            self.image = Enemy.img
        else:
            self.image = Enemy.base
            font = pygame.font.Font(None, 50)
            text = font.render(self.nick, True, (255, 255, 255))
            rct = text.get_rect()
            rct.center = (50, 50)
            rct.size = (100, 100)
            self.image.blit(text, rct)

    def update(self, *args, **kwargs) -> None:
        return


enemy = Enemy(Scene, "")
enemy.rect.center = (100000, 100000)


class Player(Sprite):
    try:
        img = pygame.image.load("data/player.png").convert_alpha()
        img = pygame.transform.scale(img, (100, 100))
        base = pygame.Surface((100, 100))
        base.fill("blue")
    except Exception as e:
        print(e)
        sys.exit(-1)

    def __init__(self, group, nicknam):
        super().__init__(group)
        self.image = Player.base
        font = pygame.font.Font(None, 50)
        text = font.render(self.nick, True, (255, 255, 255))
        rct = text.get_rect()
        rct.center = (50, 50)
        rct.size = (100, 100)
        self.image.blit(text, rct)
        self.rect = self.image.get_rect()
        self.rect.center = Vector2(*size) // 2
        self.move = Vector2(0, 0)
        self.nick = nicknam
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
        if self.ulta and enemy.ulta:
            pass
        elif enemy.ulta:
            move = Vector2(*enemy.rect.center) - Vector2(*self.rect.center)
            if move.length() < 1:
                return
            move = move.normalize() * 10
            move = (round(move.x), round(move.y))
            self.rect = self.rect.move(*move)


def main():
    running, fps = True, 60
    clock = pygame.time.Clock()

    player = Player(Scene, input())

    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        ClientSocket.send(str.encode(f'[{client_id}, {player.rect.center}, {player.ulta}, {player.nick}]'))
        log_de = eval(ClientSocket.recv(2048).decode('utf-8'))
        if len(log_de) > 1:
            if enemy.id == -999:
                enemy.id = 1 - client_id
                print(enemy.id)
            log = log_de[1 - enemy.id]
            enemy.rect.center = log[1]
            enemy.ulta = log[2]
            enemy.nick = log[3]
            enemy.is_ulta()

        Scene.update(events)
        screen.fill("black")
        Scene.draw(screen)
        pygame.display.flip()
        clock.tick(fps)
    pygame.quit()
    ClientSocket.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
