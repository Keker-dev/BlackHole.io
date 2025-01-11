import socket, os
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


# -----ИНФОРМАЦИЯ ОБ ИГРОВОЙ КОМНАТЕ------
players = []

# -----ИНИЦИАЛИЗАЦИЯ СЕРВЕРА-------
ServerSocket = socket.socket()
host, port = '26.68.85.151', 7891  # <----- IP адрес сервера
ThreadCount = -1  # <--- количество подключённых игроков
try:
    ServerSocket.bind((host, port))  # <----- привязываем сервер к IP
    print('Сервер в сети!')
except socket.error as e:
    print(str(e))

ServerSocket.listen(20)


def threaded_client(connection):  # <----- Цикл общения клиента и сервера
    players.append(Player(ThreadCount))  # <------ Добавляем клиента в игровую комнату | [ClientID, x, y]
    connection.send(str.encode(str(ThreadCount)))  # <------- Отправляем клиенту его ID

    cnt_ers = 0
    this_client_id = ThreadCount
    while True:  # <------ Цикл общения клиента и сервера во время игры

        log_en = connection.recv(2048)

        log_de = log_en.decode('utf-8')  # <------ Получаем информацию о передвижении/изменении его данных от клиента
        try:
            log = eval(log_de)
            players[log[0] - 1] = Player(log[0], log[1], log[2], log[3])
        except Exception as e:
            pass
        try:
            connection.send(str.encode(str(players)))  # <------- Отправляем клиенту информацию о всей игровой комнате
            cnt_ers = 0
            print(players)
        except Exception as e:
            cnt_ers += 1
            if cnt_ers >= 10:
                break
    print(f"Remove player with id={this_client_id}")
    players[this_client_id - 1].pos = (50000, 50000)
    players[this_client_id - 1].ulta = False


while True:
    Client, address = ServerSocket.accept()  # <------- Устанавливаем соединение с клиентом
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    print(type(Client))
    ThreadCount += 1  # <----- увеличиваем счётчик подключённых клиентов
    start_new_thread(threaded_client, (Client,))  # <------- Открываем цикл общения с клиентом (функция threaded_client)
    print('Thread Number: ' + str(ThreadCount))

ServerSocket.close()
