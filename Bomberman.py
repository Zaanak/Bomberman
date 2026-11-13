import pygame as pg
from enum import Enum
import random
import math

# Инициализация игры 
pg.init()

# Константы игры
CELL_SIZE = 56
HALF_CELL_SIZE = CELL_SIZE // 2

# Карта уровня: 1 - стены, 2 - разрушаемые блоки, -1 - где можно ходить, 3 - выход, 9 - неразрушаеммыеблоки на карте
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

# Функция «выравнивания» игрока по центру клетки (чтобы он шел ровно по сетке)
def clip_mid(value):
    cell = value // CELL_SIZE # value - координата в пикселях
    return cell*CELL_SIZE+HALF_CELL_SIZE

# Проверка, находится ли игрок достаточно близко к центру клетки, чтобы повернуть
def is_centered(x, y, direction):
    if direction in (Direction.UP, Direction.DOWN):
        return abs(x % CELL_SIZE-28) < 10
    elif direction in (Direction.LEFT, Direction.RIGHT):
        return abs(y % CELL_SIZE-28) < 10

    return False

# Проверка, можно ли пройти на эту клетку (стены и блоки непроходимы)
def is_walkable(x, y):
    j = x // CELL_SIZE
    i = y // CELL_SIZE

    cell_type = LEVEL_MAP[i][j]

    if cell_type == 1 or cell_type == 2:
        return False
    else:
        return True

# Функция создания графического холста (Surface) для всей карты уровня
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

# Функция подсчета дельты времени (сколько прошло времени между кадрами)
def update_time(tick, new_tick):
    return new_tick, new_tick - tick

# Направления движения (привязаны к клавишам WASD)
class Direction(Enum):
    UP = pg.K_w
    DOWN = pg.K_s
    LEFT = pg.K_a
    RIGHT = pg.K_d

# Базовый класс для любых объектов на карте (игрок, бомба и т.д.)
class Entity:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y

# Класс персонажа (наследуется от Entity)
class Character(Entity):
    def move(self, direction):
        # Если не отцентрирован — ходить нельзя (чтобы не застревать в углах)
        if not is_centered(self.x, self.y, direction):
            return
        
        # Логика шагов с проверкой стен
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

# Класс бомбы
class Bomb(Entity):
    def __init__(self, x, y, delay=2000, range=1):
        super().__init__("Bomb", x, y)
        self.delay = delay # Таймер в миллисекундах (2 секунды)

    # Обновление таймера бомбы каждый кадр
    def update(self, tickdelta, ask_to_burn=None):
        self.delay -= tickdelta
        if self.delay < 0:
            print("Kaboom")

            # Вычисляем индексы клетки, где рванет бомба
            j = self.x // CELL_SIZE
            i = self.y // CELL_SIZE

            # Уничтожаем блоки вокруг (крестом)
            if ask_to_burn != None:
                ask_to_burn(i, j)
                ask_to_burn(i - 1, j) 
                ask_to_burn(i + 1, j) 
                ask_to_burn(i, j - 1) 
                ask_to_burn(i, j + 1) 

    # Отрисовка бомбы и красивого белого таймера-дуги поверх переданного холста
    def render(self, surface):
        # Рисуем саму черную бомбу
        pg.draw.circle(surface, "black", (self.x, self.y), HALF_CELL_SIZE)

        # Ограничивающий прямоугольник для дуги таймера
        arc_rect = (
            self.x - HALF_CELL_SIZE,
            self.y - HALF_CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE,
                    )
        
        # Считаем прогресс таймера от 1.0 до 0.0 и переводим в радианы для pg.draw.arc
        progress = max(0.0, self.delay / 2000.0)
        stop_angle = progress * 2 * math.pi

        if stop_angle > 0:
            pg.draw.arc(surface, "white", arc_rect, 0, stop_angle, width=3)
            print(self.x, self.y)

# Главный класс игры, который управляет процессом, игроком и бомбами  
class Game:

    # Обработка нажатий клавиш и логика кадра
    def process(self, events, tickdelta):
        if self.finished:
            return

        keys = pg.key.get_pressed()

        # Движение игрока
        if keys[pg.K_w]:
            self.player.move(Direction.UP)
        elif keys[pg.K_s]:
            self.player.move(Direction.DOWN)
        elif keys[pg.K_d]:
            self.player.move(Direction.RIGHT)
        elif keys[pg.K_a]:
            self.player.move(Direction.LEFT)

        # Поставить бомбу по нажатию клавиши 'E' (если её еще нет на поле)
        if keys[pg.K_e]:
            self.bomb = Bomb(clip_mid(self.player.x), clip_mid(self.player.y))

        # Проверка, наступил ли игрок на финиш (черная клетка = 3)
        j = game.player.x // CELL_SIZE
        i = game.player.y // CELL_SIZE
        cell_type = LEVEL_MAP[i][j]

        if cell_type == 3:
            self.finished = True

        # Если бомба существует — обновляем её таймер
        if self.bomb:
            self.bomb.update(tickdelta, self.burn_tile)
            # Когда время вышло (delay < 0), удаляем бомбу
            if self.bomb.delay < 0:
                self.bomb = None

    # Логика взрыва блоков и гибели игрока
    def burn_tile(self, i, j):
        cell_type = LEVEL_MAP[i][j]

        player_j = game.player.x // CELL_SIZE
        player_i = game.player.y // CELL_SIZE

        if cell_type == 2:
            LEVEL_MAP[i][j] = -1 # Уничтожаем разрушаемый блок
        if player_j == j and player_i == i:
            self.finished = True # Игрок погиб от взрыва

        print("burning tile", i, j, "|", player_j, player_i)

    # Сборка всей графики кадра в единый холст
    def render(self):
        # 1. Рисуем карту
        surface = draw_map(LEVEL_MAP)
        # 2. Рисуем игрока (красный круг)
        pg.draw.circle(surface, "red", (self.player.x, self.player.y), HALF_CELL_SIZE)

        # 3. Если есть бомба — рисуем её поверх карты и игрока
        if self.bomb is not None:
            self.bomb.render(surface)
        return surface # Возвращаем готовый экран для отрисовки


    def __init__(self):
        self.finished = False
        self.bomb = None # Изначально бомбы на поле нет
        self.player = Character("Bomberman", 84, 84) # Спавним игрока

        # Генерация разрушаемых блоков (9 заменяем на 2 или -1)
        for i in range(11):
            for j in range(15):
                cell_type = LEVEL_MAP[i][j]

                if cell_type == 9:
                    if random.random() > 0.9:
                        LEVEL_MAP[i][j] = 2
                    else:
                        LEVEL_MAP[i][j] = -1

# --- ЗАПУСК ИГРЫ ---
screen = pg.display.set_mode((15*CELL_SIZE, 11*CELL_SIZE))
running = True
game = Game()
tick = pg.time.get_ticks()

# Главный игровой цикл
while running and not game.finished:
    new_tick = pg.time.get_ticks()
    tick, tickdelta = update_time(tick, new_tick)
    events = pg.event.get()
    for event in events:
        if event.type == pg.QUIT:
            running = False

    screen.fill("orange") # Очищаем экран
    game.process(events, tickdelta) # 1. Считаем логику и нажатия
    rendered = game.render() # 2. Рендерим всю графику в холст
    screen.blit(rendered, (0,0)) # 3. Выводим холст на реальный монитор

    pg.display.flip()


pg.quit()
