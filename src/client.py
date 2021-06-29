import socket
import pickle
import pygame
import math
from settings import *
import player

HEADER = 64
FORMAT = 'utf-8'
DISCONNECT_MSG = "DISCONNECT"

SERVER = socket.gethostbyname(socket.gethostname())
PORT = 48645

ADDR = (SERVER, PORT)

current = "welcome"

pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))

name = ""
killed_by = ""


def welcome(screen):
    global die, name
    big_font = pygame.font.Font('Roboto.ttf', 72)
    medium_font = pygame.font.Font('Roboto.ttf', 48)
    small_font = pygame.font.Font('Roboto.ttf', 28)

    header = big_font.render("Dominations", True, (0, 0, 0))
    header_rect = header.get_rect()
    header_rect.center = (screen_width // 2, 50)

    space = small_font.render("press enter to begin", True, (0, 0, 0))
    space_rect = space.get_rect()
    space_rect.center = (screen_width // 2, 300)

    running = True

    die_text = medium_font.render(f"You were killed by {killed_by}", True, (0, 0, 0))
    die_rect = die_text.get_rect()
    die_rect.center = (screen_width // 2, 500)

    name_font = pygame.font.Font('Roboto.ttf', 30)
    no_name_text = name_font.render("enter your name", True, (128, 128, 128))
    clock = pygame.time.Clock()
    cursor_blinking = True
    cursor_frame = 0

    while running:
        clock.tick(30)
        screen.fill((255, 255, 255))
        screen.blit(header, header_rect)
        pygame.draw.rect(screen, (138, 138, 138), ((screen_width - 500) // 2, 200, 500, 35), 2)

        if name == "":
            screen.blit(no_name_text, ((screen_width - 495) // 2, 198))

        else:
            screen.blit(space, space_rect)
            name_text = name_font.render(name, True, (0, 0, 0))
            name_rect = name_text.get_rect()
            name_rect.topleft = ((screen_width - 495) // 2, 200)
            screen.blit(name_text, name_rect)

            if cursor_blinking:
                pygame.draw.rect(screen, (0, 0, 0), (*name_rect.topright, 2, 34))

                if not cursor_frame % 30:
                    cursor_frame %= 30
                    cursor_blinking = False

            else:
                if not cursor_frame % 15:
                    cursor_frame %= 15
                    cursor_blinking = True

            cursor_frame += 1

        if die:
            screen.blit(die_text, die_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                die = False
                return "quit"

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_RETURN:
                    if name != "":
                        die = False
                        return "game"

                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    name += event.unicode

        pygame.display.update()


def game(screen):
    global die, killed_by
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # connecting
    client.connect(ADDR)

    def send_message(message, conn):
        message_length = len(message)
        send_length = str(message_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        conn.send(send_length)
        conn.send(message)

    send_message(pickle.dumps(name), client)
    pygame.init()

    data_size = int(client.recv(HEADER))
    this_player = pickle.loads(client.recv(data_size))  # recieve ur pos

    message = pickle.dumps(this_player)
    message_length = len(message)
    send_length = str(message_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    data = pickle.loads(client.recv(int(client.recv(HEADER))))  # Get all players
    players = data[0][:-1]
    particles = data[1]

    font = pygame.font.Font('Roboto.ttf', 50)
    tiny_font = pygame.font.Font('Roboto.ttf', 15)
    name_text = tiny_font.render(name, True, (0, 0, 0))
    name_rect = name_text.get_rect()

    def draw_this_player(self, screen, x, y):
        name_rect.center = x, y - self.radius - 10
        screen.blit(name_text, name_rect)
        pygame.draw.circle(screen, (0, 255, 0), (x, y), self.radius)

    def draw_grid(screen):
        SQUARE_SIDE_LENGTH = 80
        colour = (50, 50, 50)
        x_args = [int(this_player.g_offset[0]), screen_width, 0, screen_height]
        y_args = [int(this_player.g_offset[1]), screen_height, 0, screen_width]

        if this_player.x < half_screen_width:
            x_args[0] = int(half_screen_width - this_player.x)
            y_args[2] = int(half_screen_width - this_player.x)

        elif this_player.x > board_width - half_screen_width:
            x_args[1] = int(half_screen_width + int(board_width - this_player.x)) + 2
            y_args[3] = int(half_screen_width + int(board_width - this_player.x)) + 1

        if this_player.y < half_screen_height:
            y_args[0] = int(half_screen_height - this_player.y)
            x_args[2] = int(half_screen_height - this_player.y)

        elif this_player.y > board_height - half_screen_height:
            y_args[1] = int(half_screen_height + int(board_height - this_player.y)) + 2
            x_args[3] = int(half_screen_height + int(board_height - this_player.y)) + 1

        for x in range(x_args[0], x_args[1] + 10, SQUARE_SIDE_LENGTH):
            pygame.draw.line(screen, colour, (x, x_args[2]), (x, x_args[3]))

        for y in range(y_args[0], y_args[1] + 10, SQUARE_SIDE_LENGTH):
            pygame.draw.line(screen, colour, (y_args[2], y), (y_args[3], y))

    def draw_coords():
        s = pygame.Surface((1000, 750), pygame.SRCALPHA)  # per-pixel alpha
        s.fill((255, 255, 255, 128))
        text = font.render(f'{int(this_player.x)}, {int(this_player.y)}', True, (0, 0, 0))
        rect = text.get_rect()

        pygame.draw.rect(s, (128, 128, 128, 128), (0, 0, rect.width, rect.height), 0)

        screen.blit(s, (0, 0))
        screen.blit(text, (0, 0))

    def draw_map(screen):
        s = pygame.Surface((200, 200), pygame.SRCALPHA)
        s.fill((255, 255, 255, 128))
        pygame.draw.rect(s, (128, 128, 128, 128), (0, 0, 200, 200), 0)
        screen.blit(s, (0, screen_height - 200))

        for player in players:
            center = (player.x * 200 // board_width, (screen_height - 200) + player.y * 200 // board_height)
            pygame.draw.circle(screen, (200, 0, 0, 128), center, 3)

        center = (this_player.x * 200 // board_width, (screen_height - 200) + this_player.y * 200 // board_height)
        pygame.draw.circle(screen, (0, 200, 0), center, 3)

    def draw_players(all_players):
        to_append = ['player']
        for player in all_players:
            if macro_offset_x < player.x < macro_offset_x + screen_width:
                if macro_offset_y < player.y < macro_offset_y + screen_height:

                    effective_x = player.x - macro_offset_x
                    effective_y = player.y - macro_offset_y

                    pl_name_text = tiny_font.render(player.name, True, (0, 0, 0))
                    pl_name_rect = pl_name_text.get_rect()
                    pl_name_rect.center = effective_x, effective_y - 20

                    screen.blit(pl_name_text, pl_name_rect)
                    pygame.draw.circle(screen, (255, 0, 0), (effective_x, effective_y),player.radius)

                    if ((this_player.x - player.x) ** 2 + (
                            this_player.y - player.y) ** 2) ** 0.5 < this_player.radius - player.radius:
                        to_append.append(player)

        if len(to_append) > 1:
            this_player.message.append(to_append)

    def move_player(mouse_pos):
        mouse_pos = list(mouse_pos)
        center = [screen_width // 2, screen_height // 2]
        mouse_pos[0] -= screen_width // 2
        mouse_pos[1] -= screen_height // 2

        V_A = mouse_pos[0]
        V_B = mouse_pos[1]
        hypo = math.hypot(V_A, V_B)

        try:
            temp_x = V_A / hypo
            temp_y = V_B / hypo

            this_player.y += temp_y

            if 0 < this_player.y < board_height:
                this_player.g_offset[1] -= temp_y

            this_player.x += temp_x

            if 0 < this_player.x < board_width:
                this_player.g_offset[0] -= temp_x
        except:
            pass

    def draw_particles(screen, particles):

        to_append = []
        for particle in particles:
            if macro_offset_x < particle[0] < macro_offset_x + screen_width:
                if macro_offset_y < particle[1] < macro_offset_y + screen_height:
                    pygame.draw.circle(screen, (255, 0, 0),
                                       (particle[0] - macro_offset_x, particle[1] - macro_offset_y), 2)
                    if ((this_player.x - particle[0]) ** 2 + (
                            this_player.y - particle[1]) ** 2) ** 0.5 < this_player.radius - 2:
                        to_append.append(particles.index(particle))
                        this_player.radius = int(this_player.mass ** 0.5)
        if len(to_append) > 0:
            this_player.message.append(to_append)

    running = True

    half_screen_width = screen_width // 2
    half_screen_height = screen_height // 2
    macro_offset_x = this_player.x - half_screen_width
    macro_offset_y = this_player.y - half_screen_height
    # micro_offset_limit = 20

    clock = pygame.time.Clock()

    while running:
        clock.tick(200)
        screen.fill((255, 255, 255))
        keys = pygame.key.get_pressed()
        macro_offset_x = this_player.x - half_screen_width
        macro_offset_y = this_player.y - half_screen_height

        # Drawing
        draw_grid(screen)
        draw_players(players)
        draw_map(screen)
        draw_particles(screen, particles)
        draw_coords()

        draw_this_player(this_player, screen, half_screen_width, half_screen_height)
        pos = pygame.mouse.get_pos()
        move_player(pos)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                this_player.message = DISCONNECT_MSG

        # Network Below
        message = pickle.dumps(this_player)
        message_length = len(message)
        send_length = str(message_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        client.send(send_length)
        client.send(message)
        if running:
            try:
                data = pickle.loads(client.recv(int(client.recv(HEADER))))
                this_player, players = data[0][-1], data[0][:-1]
                particles = data[1]
            except:
                pass
        # Network Above
        if this_player.message == ['dead']:
            die = True
            killed_by = this_player.killer
            return "welcome"

        pygame.display.update()
    return "quit"


die = False
while True:

    if current == "welcome":
        current = welcome(screen)
    elif current == "game":
        current = game(screen)
    elif current == "quit":
        break

pygame.quit()
