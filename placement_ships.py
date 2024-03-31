from random import randint, random
import numpy as np
from base_classes import Ship

from deap import base
from deap import creator
from deap import tools
from deap.algorithms import varAnd


class PlacementShips:
    """Генетический алгоритм расстановки кораблей
    Формат хромосомы: [x, y, p, x, y, p, x, y, p, ... x, y, p]
    x, y - координаты начала корабля, p - ориентация корабля
    сначала идет 4-х палубный, затем 3-х палубный и т.д. type_ship = (4, 3, 3, 2, 2, 2, 1, 1, 1, 1)
    """
    POPULATION_SIZE = 200  # количество индивидуумов в популяции
    P_CROSSOVER = 0.9  # вероятность скрещивания
    P_MUTATION = 0.5  # вероятность мутации индивидуума
    MAX_GENERATIONS = 50  # максимальное количество поколений
    HALL_OF_FAME_SIZE = 1

    def __init__(self, board_size=10):
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)

        self._size = board_size  # Размер игрового поля
        self._n_ships = 10  # Количество кораблей
        # Список подбитых кораблей согласно шаблону type_ship = (4, 3, 3, 2, 2, 2, 1, 1, 1, 1)
        self.is_destroyed_list = [False] * self._n_ships
        self._length_chromo = self._n_ships * 3  # Длина хромосомы
        # Хромосома с координатами подбитых кораблей, координаты целых кораблей равны 0
        self.destroyed_ships_chromo = [0] * self._length_chromo
        self.shot_coords = set()  # Массив координат выстрелов
        self.move_game = False  # Корабли перемещаются True или нет False

    def modify_individual(self, individual: 'Individual') -> 'Individual':
        """Функция модификации хромосомы. Не позволяет изменять координаты подбитых кораблей"""
        res = []

        for *ind, des in zip(*[iter(individual)] * 3, *[iter(self.destroyed_ships_chromo)] * 3, self.is_destroyed_list):
            if des:
                res.extend(ind[3:])
            else:
                res.extend(ind[:3])

        individual[:] = res

        return individual

    def random_ship(self, total: int):
        chromo = []
        for _ in range(total):
            chromo.extend([randint(0, self._size - 1), randint(0, self._size - 1), randint(1, 2)])

        chromo = self.modify_individual(chromo)
        return creator.Individual(chromo)

    def show_board(self, sh: list):
        board = [[0 for _ in range(self._size)] for _ in range(self._size)]
        for x, y in self.shot_coords:
            board[y][x] = '•'
        for s in sh:
            y, x = s.get_start_coords()
            if s.tp == 2:
                for i in range(s.length):
                    if x + i > self._size - 1:
                        break
                    board[x + i][y] = s.length

            if s.tp == 1:
                for i in range(s.length):
                    if y + i > self._size - 1:
                        break
                    board[x][y + i] = s.length

        for b in board:
            print(*b)

    @staticmethod
    def generate_ships(individual: 'Individual') -> list:
        ships = []
        type_ship = (4, 3, 3, 2, 2, 2, 1, 1, 1, 1)  # Список возможных кораблей

        for x, y, o, t in zip(*[iter(individual)] * 3, type_ship):
            ships.append(Ship(t, o, x, y))

        return ships

    def ships_fitness(self, individual: 'Individual') -> tuple:
        """Функция принадлежности. Определяет приспособленность отдельной особи"""
        ships = self.generate_ships(individual)
        res = 0
        for i, ship in enumerate(ships):
            if not self.move_game and not self.is_destroyed_list[i]:
                res += ship.is_on_shot_coords(self.shot_coords)
            res += ship.is_out_pole(self._size)
            res += sum([ship.is_collide(obj) for obj in ships if obj != ship])
        return res,

    @staticmethod
    def cx_one_point(child1, child2):
        """Одноточечный кроссинговер"""
        a = randint(3, len(child1) - 3)
        while a % 3 != 0:
            a = randint(3, len(child1) - 3)
        child1[a:], child2[a:] = child2[a:], child1[a:]
        return child1, child2

    def mut_ships(self, individual, indpb):
        """Мутация"""
        for i in range(len(individual)):
            if random() < indpb:
                individual[i] = randint(1, 2) if (i + 1) % 3 == 0 else randint(0, self._size - 1)

        return individual,

    def create_toolbox(self):
        # Initialize the toolbox
        toolbox = base.Toolbox()
        toolbox.register("randomShip", self.random_ship, self._n_ships)
        toolbox.register("populationCreator", tools.initRepeat, list, toolbox.randomShip)

        # toolbox.register("modifyIndividual", self.modify_individual)
        # toolbox.register("modifyPopulation", tools.initRepeat, list, toolbox.modifyIndividual)

        # Register the evaluation operator
        toolbox.register("evaluate", self.ships_fitness)

        # Register the crossover operator
        toolbox.register("mate", self.cx_one_point)

        # Register a mutation operator
        toolbox.register("mutate", self.mut_ships, indpb=1.0 / self._length_chromo)

        # Operator for selecting individuals for breeding
        toolbox.register("select", tools.selTournament, tournsize=3)

        return toolbox

    def ea_simple_elitism(self, population, toolbox, cxpb, mutpb, ngen, stats=None,
                          halloffame=None, verbose=__debug__):
        """Переделанный алгоритм eaSimple с элементом элитизма"""

        logbook = tools.Logbook()
        # logbook.header = ['gen', 'nevals'] + (stats.fields if stats else [])

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in population if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        if halloffame is not None:
            halloffame.update(population)

        hof_size = len(halloffame.items) if halloffame.items else 0

        record = stats.compile(population) if stats else {}
        logbook.record(gen=0, nevals=len(invalid_ind), **record)
        if verbose:
            print(logbook.stream)

        # Begin the generational process
        n_generation = 0
        min_value = 1000
        # while n_generation < ngen and min_value > 0:
        while min_value > 0:
            n_generation += 1
            # Select the next generation individuals
            offspring = toolbox.select(population, len(population) - hof_size)

            # Vary the pool of individuals
            offspring = varAnd(offspring, toolbox, cxpb, mutpb)

            # offspring = toolbox.modifyPopulation(self.POPULATION_SIZE)
            offspring = [self.modify_individual(item) for item in offspring]

            # Evaluate the individuals with an invalid fitness
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            offspring.extend(halloffame.items)

            # Update the hall of fame with the generated individuals
            if halloffame is not None:
                halloffame.update(offspring)

            # Replace the current population by the offspring
            population[:] = offspring

            # Append the current generation statistics to the logbook
            record = stats.compile(population) if stats else {}
            logbook.record(gen=n_generation, nevals=len(invalid_ind), **record)
            min_values = logbook.select('min')
            min_value = min(min_values)
            if verbose:
                print(logbook.stream)

        return population, logbook

    def main(self):
        toolbox = self.create_toolbox()

        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("min", np.min)

        population = toolbox.populationCreator(self.POPULATION_SIZE)

        hof = tools.HallOfFame(self.HALL_OF_FAME_SIZE)

        population, logbook = self.ea_simple_elitism(population, toolbox,
                                                     cxpb=self.P_CROSSOVER,
                                                     mutpb=self.P_MUTATION,
                                                     ngen=self.MAX_GENERATIONS,
                                                     halloffame=hof,
                                                     stats=stats,
                                                     verbose=False)

        minFitnessValues = logbook.select("min")

        best = hof.items[0]
        # print(f'{best = }')
        # ships = self.generate_ships(best)
        # self.show_board(ships)
        # print(self.shot_coords)
        return best


if __name__ == "__main__":
    sf = PlacementShips(10)
    sf.is_destroyed_list = [False, True, True, True, True, True, False, False, False, False]
    # sf.ships_coords = [2, 9, 1, 2, 7, 1, 4, 2, 1, 2, 1, 2, 4, 0, 1, 8, 6, 1, 0, 0, 2, 2, 4, 2, 9, 1, 1, 9, 8, 1]
    sf.destroyed_ships_chromo = [2, 7, 1, 0, 3, 2, 7, 3, 2, 5, 0, 2, 2, 4, 1, 3, 0, 2, 0, 1, 2, 7, 7, 1, 5, 5, 1, 5, 3, 2]
    sf.shot_coords = {(1, 7), (1, 3), (2, 3), (3, 3), (4, 3), (7, 1), (3, 8), (6, 8), (9, 3), (3, 9), (6, 9), (2, 6),
                      (6, 3), (7, 2), (7, 6)}
    sf.main()
