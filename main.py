from string import ascii_lowercase
import base_classes
import radar
from placement_ships import PlacementShips


def show(size, current_player, next_player) -> None:
    """Вывод в консоль игровых полей обоих игроков"""
    # Создаем временное пустое объединенное поле
    combine_board = [[0 for _ in range(size * 2 + 1)] for _ in range(size)]
    if current_player.is_ai:
        computer_board = current_player.player_board
        human_board = next_player.player_board
    else:
        human_board = current_player.player_board
        computer_board = next_player.player_board
    # Обновляем игровое поле для игрока и помечаем все клетки открытыми (Свое поле мы можем видеть)
    human_board.update_pole(False)
    # Обновляем игровое поле компьютера
    computer_board.update_pole(True)
    # Заполняем объединенное игровое поле значениями полей игрока и компьютера
    for i in range(size):
        for j in range(size):
            combine_board[i][j] = computer_board.board[i][j]
            combine_board[i][size] = ' '
            combine_board[i][j + size + 1] = human_board.board[i][j]
    # Выводим объединенное поле в консоли
    letters = '     ' + '  '.join([i for i in ascii_lowercase[0: size].upper()])
    print(letters, letters, sep='')
    for i in range(size):
        print(str(i + 1).rjust(2, ' '), end='  ')
        for j in range(size * 2 + 1):
            print(str(combine_board[i][j]).rjust(2, ' '), end=' ')
        print()
    print()

if __name__ == '__main__':
    global_size = 10  # Размер игрового поля
    move_game = True  # Будут ли перемещаться корабли

    # Инициализация генетического алгоритма
    placement_ships = PlacementShips(global_size)

    # Инициализация игроков
    current_player = base_classes.Player('Игрок', False)
    next_player = base_classes.Player('Компьютер', True)

    # Инициализация игровых полей
    current_player.player_board = base_classes.GamePole(global_size)
    next_player.player_board = base_classes.GamePole(global_size)

    # Начальная расстановка кораблей
    print(f'Расставляем корабли для {current_player.name}')
    current_player.player_board.init(placement_ships)
    print(f'Расставляем корабли для {next_player.name}')
    next_player.player_board.init(placement_ships)

    # Создаем ссылки на поле противника
    current_player.opponent_board = next_player.player_board
    next_player.opponent_board = current_player.player_board

    show(global_size, current_player, next_player)

    # Инициализация радара
    ai = radar.AI(next_player, placement_ships)
    next_player.ai = ai

    # Передаем ссылки на координаты выстрелов
    placement_ships.shot_coords = next_player.opponent_board.shot_coords
    placement_ships.move_game = move_game

    # Игровой процесс
    while True:
        if current_player.is_game_over():
            break

        print(f'Ход {current_player.name}: ', end=' ')
        # Делаем выстрел
        shot_result = current_player.do_shot()
        print('\n'.join(current_player.message))

        if not shot_result:
            print('Мимо')
            if move_game:
                next_player.player_board.move_ships()
            # Переключение игроков
            current_player, next_player = next_player, current_player

        show(global_size, current_player, next_player)
        current_player.message.clear()

    print(f'Победил {current_player.name} за {current_player.n_turns} ходов')
