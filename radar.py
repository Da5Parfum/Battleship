from random import choice
from string import ascii_lowercase
from base_classes import Cell, Ship, Player
from placement_ships import PlacementShips


class AI:
    """Определение координаты текущего хода компьютера.

      Координаты определяются по карте весов. Каждый ход выбирается случайным образом из списка клеток с самым высоким
      коэффициентом.

      Перед каждым ходом проверяется наличие раненых кораблей. Если такие находятся, то увеличиваем вес соседних
      клеток в 10 раз, а самой клетке ставится коэффициент 0.

      Если раненых кораблей нет, то вероятное расположение определяется при помощи генетического алгоритма,
      с учетом подбитых кораблей"""

    def __init__(self, ai: Player, sf: 'PlacementShips'):
        self.ai = ai  # Экземпляр класса Player. Через него получаем доступ к игровому полю и кораблям
        self.size = self.ai.player_board.size  # Размер поля
        self.radar = []  # Карта весов. Из нее компьютер будет брать координаты для стрельбы
        self.ship_formation = sf

    def get_adjacent_cells(self, ship: Ship) -> tuple:
        """Определение координат клеток вокруг раненого корабля."""
        if ship.length == 1:
            offset = (-1, 0), (0, -1), (0, 1), (1, 0)
        else:
            offset = ((-1, 0), (1, 0)) if ship.tp == Ship.HORIZONTAL else ((0, -1), (0, 1))
        agj_coords = set()
        for adj_x, adj_y in ship.get_deck_coords():
            for i, j in offset:
                if 0 <= adj_x + i < self.size and 0 <= adj_y + j < self.size and (
                        adj_x + i, adj_y + j) not in ship.get_deck_coords():
                    agj_coords.add((adj_x + i, adj_y + j))
        return tuple(agj_coords)

    @staticmethod
    def get_orientation(coordinates) -> int:
        """Определение ориентации корабля по координатам"""
        # Если известна только одна координата, то считаем корабль однопалубным
        if len(coordinates) == 1:
            return Ship.HORIZONTAL

        x1, y1 = coordinates[0]
        x2, y2 = coordinates[1]
        if x1 == x2:
            return Ship.VERTICAL
        elif y1 == y2:
            return Ship.HORIZONTAL

    @staticmethod
    def get_ship_params(ship: Ship) -> list:
        """Возвращает координаты и ориентацию подбитого корабля"""
        if ship.is_destroyed():
            return [*ship.get_start_coords(), ship.tp]
        else:
            return [0, 0, 0]

    def generate_probable_ship_location(self) -> list[Ship]:
        """Создание предполагаемых кораблей при помощи генетического алгоритма"""
        # Получаем список всех кораблей противника
        ai_ships = self.ai.opponent_board.get_ships()

        # Сохраняем координаты и ориентацию подбитых кораблей, так как это открытая информация
        self.ship_formation.is_destroyed_list = [s.is_destroyed() for s in ai_ships]
        self.ship_formation.destroyed_ships_chromo = [_ for z in list(map(self.get_ship_params, ai_ships)) for _ in z]

        return PlacementShips.generate_ships(self.ship_formation.main())

    def create_dummy_ship(self, damaged_cells: tuple) -> Ship:
        """Функция создания корабля по координатам"""
        orientation = self.get_orientation(damaged_cells)  # Определяем ориентацию корабля
        dummy_ship = Ship(len(damaged_cells), orientation)  # Создаем корабль-болванку
        dummy_ship.set_start_coords(*damaged_cells[0])  # Присваиваем ему начальные координаты

        return dummy_ship

    def generate_radar(self) -> None:
        """Генерация карты весов."""
        self.ai.opponent_board.update_pole()

        # Для начала выставляем всем клеткам 1.
        self.radar = [[1 for _ in range(self.size)] for _ in range(self.size)]

        damaged_cells = ()  # Массив координат клеток с ранеными кораблями

        # Далее проходим по всему полю и находим клетки с ранеными кораблями.
        # Самим клеткам с ранеными или уничтоженными кораблями присваиваем коэффициент 0
        for i in range(self.size):
            for j in range(self.size):
                if self.ai.opponent_board.board[j][i].value == Cell.DAMAGED:
                    damaged_cells += ((i, j),)
                    self.radar[j][i] = Cell.WATER
                if self.ai.opponent_board.board[j][i].value == Cell.DESTROYED:
                    self.radar[j][i] = Cell.WATER
                if self.ai.opponent_board.board[j][i].value == Cell.ADJACENT:
                    self.radar[j][i] = Cell.WATER

        if damaged_cells:  # Если есть раненые корабли
            dummy_ship = self.create_dummy_ship(damaged_cells)  # Создаем корабль-болванку
            # Далее находим соседние клетки вокруг корабля-болванки с условием, что
            # Если поражена только одна палуба, то корабль имеет продолжение в любой из четырех сторон,
            # по диагоналям ничего не может быть.
            # Если поражены несколько палуб, то нам уже известна ориентация корабля,
            # и продолжение может быть только в двух направлениях

            # Увеличиваем значение соседних клеток корабля-болванки в 10 раз
            for x, y in self.get_adjacent_cells(dummy_ship):
                self.radar[y][x] *= 10

            # Значения клеток, куда ранее производилась стрельба, уменьшаем на 5
            for x, y in self.ai.opponent_board.shot_coords:
                self.radar[y][x] -= 5
        else:
            # Если раненых кораблей нет, создаем предполагаемое расположение кораблей при помощи генетического алгоритма
            dummy_ships = self.generate_probable_ship_location()
            # Увеличиваем значение клеток кораблей-болванок в 5 раз
            for dm in dummy_ships:
                for dummy_x, dummy_y in dm.get_deck_coords():
                    if self.radar[dummy_y][dummy_x] == 1:
                        self.radar[dummy_y][dummy_x] *= 5

    def show_radar(self) -> None:
        """Отображает радар в консоли. Нужно только для тестов"""
        print()
        print('    ' + '  '.join([i for i in ascii_lowercase[0: self.size].upper()]))
        for i in range(self.size):
            print(str(i + 1).rjust(2, ' '), end=' ')
            for j in range(self.size):
                print(str(self.radar[i][j]).rjust(2, ' '), end=' ')
            print()
        print()

    def get_max_weight_cells(self) -> list:
        """Определение клеток с максимальным весом"""
        weights = {}
        max_weight = 0
        # Пробегаем по всем клеткам и заносим их в словарь с ключом который является значением в клетке
        # заодно запоминаем максимальное значение. Далее просто берём из словаря список координат с этим
        # максимальным значением weights[max_weight]
        for x in range(self.size):
            for y in range(self.size):
                if self.radar[x][y] > max_weight:
                    max_weight = self.radar[x][y]
                weights.setdefault(self.radar[x][y], []).append((x, y))

        return weights[max_weight]

    def get_ai_shot_coords(self) -> tuple:
        """Основная функция. Определяет координату для выстрела"""
        self.generate_radar()
        # self.show_radar()
        return choice(self.get_max_weight_cells())
