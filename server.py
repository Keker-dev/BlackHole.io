import socket
import os
import random
import sqlite3
from _thread import *

test_mode = input("Test mode(Enter=False, y=True): ")


class Player:
    def __init__(self, id_thread, pos=(0, 0), ulta=False, nickname="", is_dead=False):
        self.id = id_thread
        self.pos = pos
        self.ulta = ulta
        self.nick = nickname
        self.is_dead = is_dead

    def __str__(self):
        return f"({self.id}, {self.pos}, {self.ulta}, '{self.nick}', {self.is_dead})"

    def __repr__(self):
        return f"({self.id}, {self.pos}, {self.ulta}, '{self.nick}', {self.is_dead})"


class Room:
    def __init__(self, max_players=10, mode="Base"):
        self.max_pls = max_players
        self.players = []
        self.mode = mode
        self.start = False

    def start_match(self):
        self.start = True
        """poses = [(-8000, -8000), (0, -8000), (8000, -8000), (-8000, 0), (-3000, 0), (3000, 0), (8000, 0), (-8000, 8000),
                 (0, 8000), (8000, 8000)]
        for i in self.players:
            i.pos = poses.pop(random.randint(0, len(poses) - 1))"""

    def add(self, obj):
        if len(self.players) < self.max_pls:
            self.players.append(obj)
        if len(self.players) == self.max_pls:
            self.start_match()

    def info(self):
        return str(self.players)

    def is_search(self):
        return not self.start

    def find_player(self, id_pl):
        res = False
        for i in self.players:
            if i.id == id_pl:
                res = i
                break
        return res


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
    cnt_ers, cur_pl = 0, None
    id_room = -1
    # Цикл общения клиента и сервера во время игры
    while True:
        try:
            log = connection.recv(2048).decode('utf-8').split(" ", maxsplit=1)
        except ConnectionAbortedError:
            break
        if not cur_pl and log[0] == "reg":
            id_pl, logn, pasw = eval(log[1])
            pl = cur.execute(f"""SELECT Login, Password, Online, Id FROM Users WHERE Login = '{logn}'""").fetchall()
            if len(pl) and pl[0][2] == 0 and pl[0][1] == pasw:
                connection.send(str.encode(f"reg True {pl[0][3]}"))
                cur_pl = [id_pl, logn, pasw]
                cur.execute(f"UPDATE Users SET Online = 1 WHERE Id = {id_pl} AND Password = '{pasw}'")
            elif not len(pl):
                pl = list(map(lambda a: a[0], cur.execute(f"SELECT Id FROM Users").fetchall()))
                if not pl:
                    pl = [0]
                pl = max(pl)
                cur.execute("INSERT INTO Users(Id, Login, Password, Online, Stats) VALUES(?, ?, ?, ?, ?)",
                            [pl, logn, pasw, 1, ""])
                cur_pl = [pl, logn, pasw]
                connection.send(str.encode(f"reg True {pl}"))
            else:
                connection.send(str.encode(f"reg False 0"))
            con.commit()
        if log[0] == "play" and id_room == -1 and cur_pl:
            id_pl, nick, play_mode = eval(log[1])
            for i, rm in enumerate(rooms):
                if rm.mode == play_mode and rm.is_search() and not rm.find_player(id_pl):
                    id_room = i
                    rm.add(Player(id_pl, nickname=nick))
                    break
            if id_room == -1:
                id_room = len(rooms)
                rooms.append(Room(2 if test_mode else 10, play_mode))
                rooms[id_room].add(Player(id_pl, nickname=nick))
            connection.send(str.encode(f"play [True, {id_room}, {rooms[id_room].is_search()}]"))
            cur.execute(f"UPDATE Users SET Online = 2 WHERE Id = {id_pl}")
            con.commit()
        if log[0] == "check_room" and id_room != -1 and cur_pl:
            connection.send(str.encode(
                f"check_room [{rooms[id_room].is_search()}, {len(rooms[id_room].players)}, {rooms[id_room].max_pls}]"))
        if log[0] == "move" and cur_pl:
            new_pos, new_ult, new_dead = eval(log[1])
            pl = rooms[id_room].find_player(cur_pl[0])
            pl.pos, pl.ulta, pl.is_dead = new_pos, new_ult, new_dead
            connection.send(str.encode(f"move {rooms[id_room].info()}"))
            print(rooms[id_room].info())
        if log[0] == "logout" and cur_pl:
            cur.execute(f"UPDATE Users SET Online = 0 WHERE Id = {cur_pl[0]}")
            con.commit()
            print(f"Set offline player with id = {cur_pl[0]}")
            if id_room != -1:
                rooms[id_room].find_player(cur_pl[0]).is_dead = True
            cur_pl = None
            id_room = -1
        # Проверка подключения
        try:
            connection.send(str.encode("0"))
        except Exception as e:
            print(e)
            break
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
    if cur_pl:
        cur.execute(f"UPDATE Users SET Online = 0 WHERE Id = {cur_pl[0]}")
        con.commit()
        print(f"Set offline player with id = {cur_pl[0]}")
        if id_room != -1:
            rooms[id_room].find_player(cur_pl[0]).is_dead = True
    con.close()


while True:
    Client, address = ServerSocket.accept()  # <------- Устанавливаем соединение с клиентом
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    print(type(Client))
    ThreadCount += 1  # <----- увеличиваем счётчик подключённых клиентов
    start_new_thread(threaded_client, (Client,))  # <------- Открываем цикл общения с клиентом (функция threaded_client)
    print('Thread Number: ' + str(ThreadCount))

ServerSocket.close()
