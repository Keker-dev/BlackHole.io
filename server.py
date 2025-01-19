import socket
import os
import random
import sqlite3
from _thread import *


class Player:
    def __init__(self, id_thread, pos=(0, 0), ulta=False, nickname=""):
        self.id = id_thread
        self.pos = pos
        self.ulta = ulta
        self.nick = nickname

    def __str__(self):
        return f"({self.id}, {self.pos}, {self.ulta}, {self.nick})"

    def __repr__(self):
        return f"({self.id}, {self.pos}, {self.ulta}, {self.nick})"


class Room:
    def __init__(self, max_players=10, mode=False):
        self.max_pls = max_players
        self.players = []
        self.mode = mode
        self.start = False

    def start_match(self):
        self.start = True
        poses = [(-8000, -8000), (0, -8000), (8000, -8000), (-8000, 0), (-3000, 0), (3000, 0), (8000, 0), (-8000, 8000),
                 (0, 8000), (8000, 8000)]
        for i in self.players:
            i.pos = poses.pop(random.randint(0, len(poses) - 1))

    def add(self, obj):
        if len(self.players) < self.max_pls:
            self.players.append(obj)

    def info(self):
        return str(self.players)

    def update_pl(self, pl_id, *args):
        pl = [i for i in range(len(self.players)) if self.players[i].id == pl_id]
        if pl:
            self.players[pl[0]] = Player(pl_id, *args)


rooms = []

# Инициализация
connection_db = sqlite3.connect("users.db")
cursor_db = connection_db.cursor()
cursor_db.execute(
    "CREATE TABLE IF NOT EXISTS Users (Id INTEGER, Login TEXT, Password TEXT, Online INTEGER, Stats TEXT)")
connection_db.close()

ServerSocket = socket.socket()
host, port = '26.68.85.151', 7891
ThreadCount = -1
try:
    ServerSocket.bind((host, port))
    print('Сервер в сети!')
except socket.error as e:
    print(str(e))

ServerSocket.listen(100)


def threaded_client(connection):
    con = sqlite3.connect("users.db")
    cur = con.cursor()
    cnt_ers, is_reg = 0, False
    # Цикл общения клиента и сервера во время игры
    while True:
        log = connection.recv(2048).decode('utf-8').split(" ", maxsplit=1)
        if log[0] == "reg":
            logn, pasw = eval(log[1])
            pl = cur.execute(f"""SELECT Login, Password, Online, Id FROM Users 
            WHERE Login = '{logn}' AND Password = '{pasw}'""").fetchall()
            if len(pl) == 1 and pl[0][2] == 0:
                connection.send(str.encode(f"reg {pl[0][3]}"))
                cur.execute(f"UPDATE Users SET Online = 1 WHERE Login = '{logn}' AND Password = '{pasw}'")
            elif len(pl) == 0:
                pl = list(map(lambda a: a[0], cur.execute(f"SELECT Id FROM Users").fetchall()))
                if not pl:
                    pl = [0]
                pl = max(pl)
                cur.execute("INSERT INTO Users(Id, Login, Password, Online, Stats) VALUES(?, ?, ?, ?, ?)",
                            [pl, logn, pasw, 1, ""])
                connection.send(str.encode(f"reg {pl}"))
            else:
                connection.send(str.encode(f"reg -1"))
        con.commit()
        # try:
        #     log = eval(log_de)
        #     players[log[0] - 1] = Player(log[0], log[1], log[2], log[3])
        # except Exception as e:
        #     pass
        # try:
        #     connection.send(str.encode(str(players)))  # <------- Отправляем клиенту информацию о всей игровой комнате
        #     cnt_ers = 0
        # except Exception as e:
        #     cnt_ers += 1
        #     if cnt_ers >= 10:
        #         break
    print(f"Remove player with id={this_client_id}")
    players[this_client_id - 1].pos = (50000, 50000)
    players[this_client_id - 1].ulta = False
    con.close()


while True:
    Client, address = ServerSocket.accept()  # <------- Устанавливаем соединение с клиентом
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    print(type(Client))
    ThreadCount += 1  # <----- увеличиваем счётчик подключённых клиентов
    start_new_thread(threaded_client, (Client,))  # <------- Открываем цикл общения с клиентом (функция threaded_client)
    print('Thread Number: ' + str(ThreadCount))

ServerSocket.close()
