"""Техническое задание
В программе необходимо объявить два класса:

Ship - для представления кораблей;
GamePole - для описания игрового поля.

Класс Ship
Класс Ship должен описывать корабли набором следующих параметров:

x, y - координаты начала расположения корабля (целые числа);
length - длина корабля (число палуб: целое значение: 1, 2, 3 или 4);
tp - ориентация корабля (1 - горизонтальная; 2 - вертикальная).

Объекты класса Ship должны создаваться командами:

ship = Ship(length)
ship = Ship(length, tp)
ship = Ship(length, tp, x, y)
По умолчанию (если не указывается) параметр tp = 1, а координаты x, y равны None.

В каждом объекте класса Ship должны формироваться следующие локальные атрибуты:

_x, _y - координаты корабля (целые значения в диапазоне [0; size), где size - размер игрового поля);
_length - длина корабля (число палуб);
_tp - ориентация корабля;
_is_move - возможно ли перемещение корабля (изначально равно True);
_cells - изначально список длиной length, состоящий из единиц (например, при length=3, _cells = [1, 1, 1]).

Список _cells будет сигнализировать о попадании соперником в какую-либо палубу корабля. Если стоит 1,
то попадания не было, а если стоит значение 2, то произошло попадание в соответствующую палубу.

При попадании в корабль (хотя бы одну его палубу), флаг _is_move устанавливается в False
и перемещение корабля по игровому полю прекращается.

В самом классе Ship должны быть реализованы следующие методы (конечно, возможны и другие, дополнительные):

set_start_coords(x, y) - установка начальных координат (запись значений в локальные атрибуты _x, _y);
get_start_coords() - получение начальных координат корабля в виде кортежа x, y;
move(go) - перемещение корабля в направлении его ориентации на go клеток
           (go = 1 - движение в одну сторону на клетку; go = -1 - движение в другую сторону на одну клетку);
            движение возможно только если флаг _is_move = True;
is_collide(ship) - проверка на столкновение с другим кораблем ship
                   (столкновением считается, если другой корабль или пересекается с текущим или просто соприкасается,
                    в том числе и по диагонали); метод возвращает True,
                    если столкновение есть и False - в противном случае;
is_out_pole(size) - проверка на выход корабля за пределы игрового поля
                    (size - размер игрового поля, обычно, size = 10);
                     возвращается булево значение True, если корабль вышел из игрового поля
                    и False - в противном случае;

С помощью магических методов __getitem__() и __setitem__() обеспечить доступ к коллекции _cells следующим образом:

value = ship[indx] # считывание значения из _cells по индексу indx (индекс отсчитывается от 0)
ship[indx] = value # запись нового значения в коллекцию _cells

Класс GamePole
Следующий класс GamePole должен обеспечивать работу с игровым полем. Объекты этого класса создаются командой:

pole = GamePole(size)
где size - размеры игрового поля (обычно, size = 10).

В каждом объекте этого класса должны формироваться локальные атрибуты:

_size - размер игрового поля (целое положительное число);
_ships - список из кораблей (объектов класса Ship); изначально пустой список.

В самом классе GamePole должны быть реализованы следующие методы (возможны и другие, дополнительные методы):

init() - начальная инициализация игрового поля; здесь создается список из кораблей (объектов класса Ship):
однопалубных - 4; двухпалубных - 3; трехпалубных - 2; четырехпалубный - 1
(ориентация этих кораблей должна быть случайной).

Корабли формируются в коллекции _ships следующим образом:
однопалубных - 4; двухпалубных - 3; трехпалубных - 2; четырехпалубный - 1.
Ориентация этих кораблей должна быть случайной.

Начальные координаты x, y не расставленных кораблей равны None.

После этого, выполняется их расстановка на игровом поле со случайными координатами так,
чтобы корабли не пересекались между собой.

get_ships() - возвращает коллекцию _ships;
move_ships() - перемещает каждый корабль из коллекции _ships на одну клетку (случайным образом вперед или назад)
               в направлении ориентации корабля; если перемещение в выбранную сторону невозможно
               (другой корабль или пределы игрового поля), то попытаться переместиться в противоположную сторону,
               иначе (если перемещения невозможны), оставаться на месте;
show() - отображение игрового поля в консоли
        (корабли должны отображаться значениями из коллекции _cells каждого корабля, вода - значением 0);

get_pole() - получение текущего игрового поля в виде двумерного (вложенного) кортежа размерами size x size элементов."""

from random import choice
from string import ascii_lowercase
from typing import Optional


class Cell:
    """Описание всех возможных состояний клетки игрового поля.
     (пустая, сыгранная, корабль, уничтоженный корабль, поврежденный корабль)."""
    WATER = 0
    SHIP = 1
    DAMAGED = 2
    DESTROYED = 3
    MISSED = 4
    ADJACENT = 5

    def __init__(self):
        self.value = self.WATER  # Значение клетки по умолчанию 0
        self.ship = None  # Если на клетке стоит корабль, то здесь будем хранить ссылку на него. Это упрощает поиск
        self.is_hidden = True  # Для управления видимостью. (Свои корабли мы всегда видим, а корабли противника - нет)

    def __str__(self):
        if self.is_hidden:
            self.str = {0: '0', 1: '0', 2: '□', 3: 'X', 4: '•', 5: '▪'}
            # убери комментарий и будут видны вражеские корабли
            # self.str = {0: '0', 1: '■', 2: '□', 3: 'X', 4: '•', 5: '▪'}
        else:
            self.str = {0: '0', 1: '■', 2: '□', 3: 'X', 4: '•', 5: '▪'}
        return self.str[self.value]


class Ship:
    """Представление кораблей"""
    # расположение кораблей
    HORIZONTAL = 1
    VERTICAL = 2

    def __init__(self, length, tp=1, x=None, y=None):
        self._x = x
        self._y = y  # координаты корабля (целые значения в диапазоне [0; size), где size - размер игрового поля)
        self._length = length  # длина корабля (число палуб)
        self._tp = tp  # ориентация корабля (1 - горизонтальная; 2 - вертикальная)
        self._is_move = True  # возможно ли перемещение корабля
        self._cells = [Cell.SHIP] * self._length  # изначально список длиной length, состоящий из единиц

    @property
    def tp(self):
        return self._tp

    @property
    def length(self):
        return self._length

    @property
    def cells(self):
        return self._cells

    @property
    def is_move(self):
        return self._is_move

    @is_move.setter
    def is_move(self, value):
        self._is_move = value

    def set_start_coords(self, x, y) -> None:
        """Установка начальных координат (запись значений в локальные атрибуты _x, _y)"""
        self._x = x
        self._y = y

    def get_start_coords(self) -> tuple:
        """Получение начальных координат корабля в виде кортежа x, y"""
        return self._x, self._y

    def get_deck_coords(self):
        """Возвращает кортеж координат всех палуб"""
        decks = ()
        for deck in range(self.length):
            deck_coords = (self._x + deck, self._y) if self.tp == self.HORIZONTAL else (self._x, self._y + deck)
            decks += deck_coords,

        return decks

    def is_collide(self, ship) -> bool:
        """Проверка на столкновение с другим кораблем ship (столкновением считается, если другой корабль или
            пересекается с текущим или просто соприкасается, в том числе и по диагонали);
            метод возвращает True, если столкновение есть и False - в противном случае"""

        start_x1, start_y1 = self.get_start_coords()
        end_x1, end_y1 = self.get_deck_coords()[-1]
        start_x2, start_y2 = ship.get_start_coords()
        end_x2, end_y2 = ship.get_deck_coords()[-1]
        # Если начальные координаты self находятся в пределах корабля ship
        if start_x1 - 1 <= start_x2 <= end_x1 + 1 and start_y1 - 1 <= start_y2 <= end_y1 + 1:
            return True
        # Если конечные координаты ship находятся в пределах корабля self
        if start_x1 - 1 <= end_x2 <= end_x1 + 1 and start_y1 - 1 <= end_y2 <= end_y1 + 1:
            return True

        return False

    def is_out_pole(self, size) -> bool:
        """Проверка на выход корабля за пределы игрового поля (size - размер игрового поля);
        возвращается булево значение True, если корабль вышел из игрового поля и False - в противном случае"""
        end_ship = self._x + self._length if self.tp == self.HORIZONTAL else self._y + self._length
        return self._x < 0 or self._y < 0 or end_ship > size

    def is_on_shot_coords(self, shot_coords: set) -> int:
        """Проверка попадает ли корабль на предыдущие координаты выстрелов"""
        deck_coords = set(self.get_deck_coords())
        return len(deck_coords & shot_coords)

    def move(self, go):
        """Перемещение корабля в направлении его ориентации на go клеток (go=1 - движение в одну сторону на клетку;
        go = -1 - движение в другую сторону на одну клетку); движение возможно только если флаг _is_move = True"""
        if not self.is_move:
            return

        if self.tp == self.HORIZONTAL:
            self.set_start_coords(self._x + go, self._y)
        elif self.tp == self.VERTICAL:
            self.set_start_coords(self._x, self._y + go)

    def get_index_deck_by_board_coords(self, board_x, board_y):
        """Возвращает индекс палубы по координатам игрового поля"""
        decks = self.get_deck_coords()

        return decks.index((board_x, board_y))

    def set_deck_damaged(self, x: int, y: int):
        index = self.get_index_deck_by_board_coords(x, y)
        self[index] = Cell.DAMAGED

    def is_damaged(self):
        return all([deck == Cell.DAMAGED for deck in self.cells])

    def is_destroyed(self):
        return all([deck == Cell.DESTROYED for deck in self.cells])

    def set_destroyed(self):
        for i in range(self.length):
            self[i] = Cell.DESTROYED

    def __getitem__(self, item):
        return self._cells[item]

    def __setitem__(self, key, value):
        self._cells[key] = value


class GamePole:
    """Описание игрового поля"""

    def __init__(self, size=10):
        self._size = size  # размер игрового поля
        self._ships = []  # список из кораблей (объектов класса Ship)
        self.shot_coords = set()  # массив координат клеток, по которым делались выстрелы
        self.board = tuple(tuple(Cell() for _ in range(self._size)) for _ in range(self._size))

    @property
    def size(self):
        return self._size

    def update_pole(self, hidden_cell: bool = True) -> None:
        """Обновление игрового поля. Заполнение ячеек поля соответствующими значениями"""
        # Обнуление ячеек игрового поля
        for i in range(self.size):
            for j in range(self.size):
                self.board[j][i].value = Cell.WATER
                self.board[j][i].ship = None
                self.board[j][i].is_hidden = hidden_cell

        for x, y in self.shot_coords:
            self.board[y][x].value = Cell.MISSED

        for ship in self._ships:
            x, y = ship.get_start_coords()

            if ship.tp == Ship.VERTICAL:
                for i in range(ship.length):
                    self.board[y + i][x].value = ship.cells[i]
                    self.board[y + i][x].ship = ship

            if ship.tp == Ship.HORIZONTAL:
                for i in range(ship.length):
                    self.board[y][x + i].value = ship.cells[i]
                    self.board[y][x + i].ship = ship

        # На поле противника клетки, куда заплыл корабль,
        # но по которым ранее уже стреляли, отмечаем как простреленные.
        if hidden_cell:
            for x, y in self.shot_coords:
                if self.board[y][x].value == Cell.SHIP:
                    self.board[y][x].value = Cell.MISSED

        # Помечаем клетки около подбитых кораблей
        for ship in self._ships:
            if ship.is_destroyed():
                for x, y in self.get_adjacent_coords(ship):
                    self.board[y][x].value = Cell.ADJACENT

    def get_adjacent_coords(self, ship: Ship) -> tuple:
        """Определение координат клеток вокруг корабля"""
        offset = (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)
        agj_coords = set()
        for adj_x, adj_y in ship.get_deck_coords():
            for i, j in offset:
                if 0 <= adj_x + i < self.size and 0 <= adj_y + j < self.size and (
                        adj_x + i, adj_y + j) not in ship.get_deck_coords():
                    agj_coords.add((adj_x + i, adj_y + j))
        return tuple(agj_coords)

    def get_ships(self) -> list:
        """Возвращает коллекцию _ships"""
        return self._ships

    def get_ship_by_coords(self, x, y):
        """Если в клетке по заданным координатам есть корабль, возвращает его"""
        for ship in self.get_ships():
            if (x, y) in ship.get_deck_coords():
                return ship

    def init(self, ai) -> None:
        """Начальная инициализация игрового поля"""
        self._ships = ai.generate_ships(ai.main())

    def move_ships(self) -> None:
        """Перемещает каждый корабль из коллекции _ships на одну клетку (случайным образом вперед или назад)
        в направлении ориентации корабля; если перемещение в выбранную сторону невозможно
        (другой корабль или пределы игрового поля), то попытаться переместиться в противоположную сторону,
        иначе (если перемещения невозможны), оставаться на месте"""
        for ship in self.get_ships():
            if not ship.is_move:
                continue

            directions = choice([[-1, 1], [1, -1]])  # Направление перемещения
            x, y = ship.get_start_coords()  # Сохраняем координаты корабля
            for d in directions:
                ship.move(d)  # Перемещаем корабль
                # Проверяем на столкновения и выход за границы
                if ship.is_out_pole(self.size) or any(
                        [ship.is_collide(obj) for obj in self.get_ships() if obj != ship]):
                    # Если есть столкновение или выход за границы,
                    # устанавливаем кораблю первоначальные координаты
                    ship.set_start_coords(x, y)
                else:
                    # Если перемещение удалось, выходим из цикла
                    break

    def show(self) -> None:
        """Отображение игрового поля в консоли
        (корабли должны отображаться значениями из коллекции _cells каждого корабля, вода - значением 0)
        В игре не используется."""
        self.update_pole()

        print('   ' + ' '.join([i for i in ascii_lowercase[0: self.size].upper()]))
        for i in range(self.size):
            print(str(i + 1).rjust(2, ' '), end=' ')
            for j in range(self.size):
                print(self.board[i][j], end=' ')
            print()
        print()

    def get_pole(self) -> tuple:
        """Получение текущего игрового поля в виде двумерного(вложенного) кортежа размерами size x size элементов"""

        return tuple(tuple(x) for x in self.board)


class Player:
    """Класс для представления игроков"""

    def __init__(self, name: str, is_ai: bool):
        self.name = name  # Имя игрока
        self.is_ai = is_ai  # Компьютер (True) или человек (False)
        self.message = []  # Здесь будем хранить все сообщения (попал, промазал)
        self.n_turns = 0  # Количество ходов
        self.player_board: Optional[GamePole] = None  # Игровое поле игрока
        self.opponent_board: Optional[GamePole] = None  # Игровое поле противника
        self.ai = None

    def get_shot_coords(self) -> tuple[int, int]:
        """Генерация/запрос координат выстрела"""
        if self.is_ai:
            x, y = self.ai.get_ai_shot_coords()
            # x = randint(0, self.player_board.size-1)
            # y = randint(0, self.player_board.size-1)
        else:
            while True:
                try:
                    x, y = input().lower().split()
                except ValueError:
                    print('Неверный формат данных')
                    continue
                if all((x.isdigit(), int(x) in range(1, 11), y in ascii_lowercase[:self.player_board.size])):
                    break
                print('Неверные координаты')

            # Переводим введенные координаты в координаты игрового поля
            y = ascii_lowercase.index(y)
            x = int(x) - 1

        self.message.append(f'{x + 1} {ascii_lowercase[y].upper()}')
        return y, x

    def do_shot(self) -> bool:
        """Запрашиваем координаты выстрела и проверяем попадание"""
        shot_x, shot_y = self.get_shot_coords()  # Получаем координаты выстрела

        if self.opponent_board.board[shot_y][shot_x].value == Cell.DESTROYED:
            print('В клетке уже пораженный корабль')
            self.do_shot()
        self.n_turns += 1
        self.opponent_board.shot_coords.add((shot_x, shot_y))  # Заносим координату в список выстрелов
        self.opponent_board.board[shot_x][shot_y].is_hidden = False  # Делаем клетку видимой
        wrecked_ship = self.opponent_board.get_ship_by_coords(shot_x,
                                                              shot_y)  # Если есть попадание, получаем ссылку на корабль
        if wrecked_ship:
            wrecked_ship.set_deck_damaged(shot_x, shot_y)  # Помечаем палубу корабля подбитой
            wrecked_ship.is_move = False  # Ставим запрет на перемещение
            self.message.append('Есть попадание')
            if wrecked_ship.is_damaged():  # Проверяем поражены ли все палубы корабля
                self.message.append('Подбит')
                wrecked_ship.set_destroyed()
            return True

        return False

    def is_game_over(self) -> bool:
        """Проверка окончания игры"""
        return all(s.is_destroyed() for s in self.opponent_board.get_ships())
