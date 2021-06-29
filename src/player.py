class Player:
    def __init__(self, x, y, addr, name):
        self.x = (x // 80) * 80
        self.y = (y // 80) * 80
        self.mass = 47
        self.message = []
        self.addr = addr
        self.g_offset = [0, 60]
        self.radius = int(self.mass ** 0.5) + 3
        self.name = name
        self.killer = None
