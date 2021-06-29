import pickle
import random
import socket
import threading
import time
import os

from player import Player
from settings import *

HEADER = 64
FORMAT = 'utf-8'
DISCONNECT_MSG = "DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

IP = "0.0.0.0"
PORT = int(os.getenv("PORT", 48645))
ADDR = (IP, PORT)


def get_time():
    return f"{int(time.time())}:"


print(f"{get_time()} [STARTING]")


class Data:
    particle_spawn = True
    players = []
    particles = []


CONSTANT_THREADS = 2


def generate_particle_coords():
    Data.particles.append([random.randint(0, board_width), random.randint(0, board_height)])


def check_particle_spawn(n=0):
    if (threading.active_count() - CONSTANT_THREADS) - n == 0:
        Data.particle_spawn = False
        while len(Data.particles) < 4002:
            generate_particle_coords()
        Data.particles = Data.particles[:1000]
    else:
        Data.particle_spawn = True


def handle_client(conn, addr):
    try:
        name_len = int(conn.recv(HEADER))
        name = conn.recv(name_len)
        name = pickle.loads(name)

        this_player = Player(random.randint(10, board_width), random.randint(10, board_height), addr, name)
        print(f"{get_time()}[CONNECTION ESTABLISHED] | [TOTAL CONNECTIONS: {threading.active_count() - CONSTANT_THREADS}]"
              f" | {addr} connected...")

        check_particle_spawn()
        # send player Data
        to_send = pickle.dumps(this_player)
        message_length = len(to_send)
        send_length = str(message_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        conn.send(send_length)  # sending the Length of the data
        conn.send(pickle.dumps(this_player))
        Data.players.append(this_player)

        connected = True
        try:
            while connected:
                try:
                    conn_msg = conn.recv(HEADER)
                    msg_length = int(conn_msg.decode(FORMAT))
                except Exception as e:
                    connected = False
                    Data.players.remove(this_player)
                    print(f"{get_time()} REMAINING PLAYERS {len(Data.players)}")

                if msg_length:
                    msg = conn.recv(msg_length)
                    msg = pickle.loads(msg)
                    if msg.x < 0:
                        msg.x = 0
                    elif msg.x > board_width:
                        msg.x = board_width

                    if msg.y < 0:
                        msg.y = 0
                    elif msg.y > board_height:
                        msg.y = board_height

                    if msg.g_offset[0] > 80:
                        msg.g_offset[0] = 0
                    elif msg.g_offset[0] < -80:
                        msg.g_offset[0] = 80

                    if msg.g_offset[1] > 80:
                        msg.g_offset[1] = 0
                    elif msg.g_offset[1] < -80:
                        msg.g_offset[1] = 80

                    for passed_message in msg.message:
                        if passed_message == DISCONNECT_MSG:
                            connected = False
                            Data.players.remove(this_player)
                            break

                        elif type(passed_message) == list and passed_message[0] == 'player':
                            for player in Data.players:
                                d = ((this_player.x - player.x) ** 2 + (this_player.y - player.y) ** 2) ** 0.5
                                if d < this_player.radius - player.radius:
                                    if this_player.radius > player.radius:
                                        msg.mass += player.mass
                                        player.mass = 0
                                        player.radius = 0
                                        player.killer = this_player.name

                        elif type(passed_message) == list:
                            for index in passed_message:
                                particle = Data.particles[index]
                                try:
                                    if ((msg.x - particle[0]) ** 2 + (msg.y - particle[1]) ** 2) ** 0.5 < msg.radius:
                                        msg.mass += 1
                                        Data.particles.remove(particle)
                                except:
                                    pass

                    if this_player.killer is not None:
                        this_player.message = ['dead']
                    else:
                        this_player.message = []

                    msg.radius = int(msg.mass ** 0.5)
                    this_player.x = msg.x
                    this_player.y = msg.y
                    this_player.g_offset = msg.g_offset
                    this_player.mass = msg.mass
                    this_player.radius = msg.radius
                    to_send = Data.players.copy()

                    for to_remove in to_send:
                        if to_remove.addr == this_player.addr:
                            to_send.remove(to_remove)

                    to_send.append(this_player)

                    message = pickle.dumps([to_send, Data.particles])
                    message_length = len(message)
                    send_length = str(message_length).encode(FORMAT)
                    send_length += b' ' * (HEADER - len(send_length))
                    conn.send(send_length)
                    conn.send(message)

        except Exception as e:
            print(f"{get_time()}[CONNECTION ENDED WITH {addr}] | [TOTAL CONNECTIONS: "
                  f"{threading.active_count() - (CONSTANT_THREADS + 1)}]")
            for player in Data.players:
                if player.addr == this_player.addr:
                    Data.players.remove(player)
                    break
            check_particle_spawn(1)
    except BrokenPipeError as e:
        print(f"{get_time()}[CONNECTION ENDED WITH {addr}] | [TOTAL CONNECTIONS: "
              f"{threading.active_count() - (CONSTANT_THREADS + 1)}]", f"\nReason: {e}")


def start():
    server.bind(ADDR)
    print(f"{get_time()} [SERVER IP]: {ADDR}\n")
    server.listen()

    while True:
        check_particle_spawn()
        conn, addr = server.accept()

        thread = threading.Thread(target=handle_client, args=(conn, addr,))
        thread.start()


def particle():
    for x in range(2000): generate_particle_coords()

    while True:
        generate_particle_coords()
        time.sleep(0.04)


threading.Thread(target=particle).start()

start()
