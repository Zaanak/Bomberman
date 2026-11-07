import pygame as pg
from enum import Enum
import random
import math

pg.init()

CELL_SIZE = 56
HALF_CELL_SIZE = CELL_SIZE // 2

LEVEL_MAP = [
    [+1,+1,+1,+1,+1,+1,+1,+1,+1,+1,+1,+1,+1,+1,+1,],
    [+1,-1,-1,+9,+9,+9,+9,+9,+9,+9,+9,+9,+9,+9,+1,],
    [+1,-1,+1,+9,+1,+9,+1,+9,+1,+9,+1,+9,+1,+9,+1,],
    [+1,+9,+9,+9,+9,+9,+9,+9,+9,+9,+9,+9,+9,+9,+1,],
    [+1,+9,+1,+9,+1,+9,+1,+9,+1,+9,+1,+9,+1,+9,+1,],
    [+1,+9,+9,+9,+9,+9,+9,+9,+9,+9,+9,+9,+9,+9,+1,],
    [+1,+9,+1,+9,+1,+9,+1,+9,+1,+9,+1,+9,+1,+9,+1,],
    [+1,+9,+9,+9,+9,+9,+9,+9,+9,+2,+9,+9,+9,+9,+1,],
    [+1,+9,+1,+9,+1,+9,+1,+9,+1,+9,+1,+9,+1,+3,+1,],
    [+1,+9,+9,+9,+9,+9,+9,+9,+9,+9,+9,+9,+9,+9,+1,],
    [+1,+1,+1,+1,+1,+1,+1,+1,+1,+1,+1,+1,+1,+1,+1,],
]

def clip_mid(value):
    cell = value // CELL_SIZE # value - координата в пикселях
    return cell*CELL_SIZE+HALF_CELL_SIZE

def is_centered(x, y, direction):
    if direction in (Direction.UP, Direction.DOWN):
        return abs(x % CELL_SIZE-28) < 10
    elif direction in (Direction.LEFT, Direction.RIGHT):
        return abs(y % CELL_SIZE-28) < 10

    return False

def is_walkable(x, y):
    j = x // CELL_SIZE
    i = y // CELL_SIZE

    cell_type = LEVEL_MAP[i][j]

    if cell_type == 1 or cell_type == 2:
        return False
    else:
        return True

def draw_map(LEVEL_MAP):
    surface = pg.Surface((15*CELL_SIZE, 11*CELL_SIZE), flags=pg.SRCALPHA)

    for i in range(11):
        for j in range(15):
            cell_type = LEVEL_MAP[i][j]

            if cell_type == 1:
                pg.draw.rect(surface, "grey", (j*CELL_SIZE, i*CELL_SIZE, CELL_SIZE, CELL_SIZE))
            elif cell_type == 2:
                pg.draw.rect(surface, "brown", (j*CELL_SIZE, i*CELL_SIZE, CELL_SIZE, CELL_SIZE))
            elif cell_type == -1:
                pg.draw.rect(surface, "green", (j*CELL_SIZE, i*CELL_SIZE, CELL_SIZE, CELL_SIZE))
            elif cell_type == 3:
                pg.draw.rect(surface, "black", (j*CELL_SIZE, i*CELL_SIZE, CELL_SIZE, CELL_SIZE))

    return surface

def update_time(tick, new_tick):
    return new_tick, new_tick - tick

class Direction(Enum):
    UP = pg.K_w
    DOWN = pg.K_s
    LEFT = pg.K_a
    RIGHT = pg.K_d

class Entity:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y

class Character(Entity):
    def move(self, direction):
        if not is_centered(self.x, self.y, direction):
            return

        if direction == Direction.UP:
            if is_walkable(self.x, self.y - 1 - HALF_CELL_SIZE):
                self.y -= 1
                self.x = clip_mid(self.x)
        elif direction == Direction.DOWN:
            if is_walkable(self.x, self.y + 1 + HALF_CELL_SIZE):
                self.y += 1
                self.x = clip_mid(self.x)
        elif direction == Direction.LEFT:
            if is_walkable(self.x - 1 - HALF_CELL_SIZE, self.y):
                self.x -= 1
                self.y = clip_mid(self.y)
        elif direction == Direction.RIGHT:
            if is_walkable(self.x + 1 + HALF_CELL_SIZE, self.y):
                self.x += 1
                self.y = clip_mid(self.y)

        print("=",self.x, self.y, "|", self.x // CELL_SIZE, self.y // CELL_SIZE, "|", self.x % CELL_SIZE, self.y % CELL_SIZE)


class Bomb(Entity):
    def __init__(self, x, y, delay=2000, range=1):
        super().__init__("Bomb", x, y)
        self.delay = delay
        self.range = range

    def update(self, tickdelta, ask_to_burn=None):
        self.delay -= tickdelta
        if self.delay < 0:
            print("Kaboom")

            j = self.x // CELL_SIZE
            i = self.y // CELL_SIZE

            if ask_to_burn != None:
                ask_to_burn(i, j)
                ask_to_burn(i - 1, j) 
                ask_to_burn(i + 1, j) 
                ask_to_burn(i, j - 1) 
                ask_to_burn(i, j + 1) 


class Game:
    def process(self, events, tickdelta):
        if self.finished:
            return

        keys = pg.key.get_pressed()

        if keys[pg.K_w]:
            self.player.move(Direction.UP)
        elif keys[pg.K_s]:
            self.player.move(Direction.DOWN)
        elif keys[pg.K_d]:
            self.player.move(Direction.RIGHT)
        elif keys[pg.K_a]:
            self.player.move(Direction.LEFT)

        if keys[pg.K_e]:
            self.bomb = Bomb(clip_mid(self.player.x), clip_mid(self.player.y))

        j = game.player.x // CELL_SIZE
        i = game.player.y // CELL_SIZE
        cell_type = LEVEL_MAP[i][j]

        if cell_type == 3:
            self.finished = True

        if self.bomb:
            self.bomb.update(tickdelta, self.burn_tile)
            if self.bomb.delay < 0:
                self.bomb = None

    def burn_tile(self, i, j):
        cell_type = LEVEL_MAP[i][j]

        player_j = game.player.x // CELL_SIZE
        player_i = game.player.y // CELL_SIZE

        if cell_type == 2:
            LEVEL_MAP[i][j] = -1
        if player_j == j and player_i == i:
            self.finished = True

        print("burning tile", i, j, "|", player_j, player_i)


    def render(self):

        surface = draw_map(LEVEL_MAP)
        pg.draw.circle(surface, "red", (self.player.x, self.player.y), HALF_CELL_SIZE)
        if self.bomb:
                pg.draw.circle(surface, "black", (self.bomb.x, self.bomb.y), HALF_CELL_SIZE)
                pg.draw.circle(surface, "white", (self.bomb.x, self.bomb.y), HALF_CELL_SIZE, width=3)
                print(self.bomb.x, self.bomb.y)
        return surface


    def __init__(self):
        self.finished = False
        self.bomb = None
        self.player = Character("Bomberman", 84, 84)

        for i in range(11):
            for j in range(15):
                cell_type = LEVEL_MAP[i][j]

                if cell_type == 9:
                    if random.random() > 0.9:
                        LEVEL_MAP[i][j] = 2
                    else:
                        LEVEL_MAP[i][j] = -1


screen = pg.display.set_mode((15*CELL_SIZE, 11*CELL_SIZE))
running = True
game = Game()
tick = pg.time.get_ticks()

while running and not game.finished:
    new_tick = pg.time.get_ticks()
    tick, tickdelta = update_time(tick, new_tick)
    events = pg.event.get()
    for event in events:
        if event.type == pg.QUIT:
            running = False

    screen.fill("orange")
    game.process(events, tickdelta)
    rendered = game.render()
    screen.blit(rendered, (0,0))

    pg.display.flip()


pg.quit()
