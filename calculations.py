# Андрей Аракельянц. 27.12.2017
# Задача этой программы - по данным наблюдений с сайта rp5.ru рассчитать
# скорость ветра заданной обеспеченности по каждому румбу.

from pandas import *
import matplotlib.pyplot as plt
import matplotlib.ticker as tick
import numpy


# Из набора данных создаю сводную таблицу
def create_pivot_table():
    full_observation_data = read_csv('example.csv', sep=';', header=6)
    # убираю всё лишнее из данных. Оставляю только два нужных мне столбца со
    # скоростью и направлением ветра: 'DD' и 'U' соответственно
    required_data = full_observation_data.loc[:, ['U', 'DD']]
    # добавляю вспомогательный столбец, который нужен для создания сводной
    # таблицы
    required_data_2 = required_data.assign(DD2=required_data['DD'])
    # расчитываю общее количество наблюдений
    observations_number = len(required_data_2.index)
    # создаю сводную таблицу с количеством наблюдений по каждому сочетанию
    # скорости-направления ветра (в дальнейшем называю это сочетание словом
    # "градация"). Строки таблицы - скорость ветра. Столбцы таблицы - направление ветра.
    velocity_direction_table = pandas.pivot_table(
        required_data_2, index='DD', values='DD2', columns='U', margins=True, aggfunc=numpy.size)
    # во всех ячейках без значений ставлю нули
    velocity_direction_table_2 = velocity_direction_table.fillna(value=0)
    return [velocity_direction_table_2, observations_number]


# Обрабатываю случаи штилей
def calm_processing(velocity_direction_table):
    # Нужно распределить штили равномерно по всем направлениями ветра.
    # количество колонок в таблице
    column_number = len(velocity_direction_table.columns)
    # количество штилей
    calm_cases = velocity_direction_table.loc[0, 'Штиль, безветрие']
    # количество штилей, равномерно распределённое по всем направлениями ветра
    calm_cases_per_each_direction = calm_cases / (column_number - 1)
    # записываю в каждый столбец строчки "0" количество штилей, распределённое
    # по направлениям
    velocity_direction_table.loc[0] = calm_cases_per_each_direction
    # прибавляю в строку "All" каждой таблицы количество штилей,
    # распределённое по направлениям
    velocity_direction_table.loc['All'] = velocity_direction_table.loc[
        'All'] + calm_cases_per_each_direction
    # Задача выполнена. Штили распределены равномерно по всем направлениям ветра.
    # удаляю столбец "Штиль, безветрие", потому что он не нужен
    velocity_direction_table = velocity_direction_table.drop(
        columns='Штиль, безветрие')
    return velocity_direction_table


# делаю таблицу с повторяемостью градаций в каждом румбе (таблица 3.2)
def recurrence_per_every_direction(velocity_direction_table):
    for column in velocity_direction_table.columns:
        cases_with_this_direction = velocity_direction_table.loc['All', column]
        # количество случаев с этим направлением ветра
        velocity_direction_table[column] = velocity_direction_table[
            column] / cases_with_this_direction
    # удаляю столбец "All", потому что он не нужен
    velocity_direction_table = velocity_direction_table.drop(columns='All')
    return velocity_direction_table


# делаю таблицу с продолжительностью каждой градации по каждому
# направлению (таблица 3.3)
def speed_direction_duration(velocity_direction_table):
    # рассчитываю количество строк в таблице
    raw_number = len(velocity_direction_table.iloc[:, 1])
    # обнуляю самую нижнюю строку таблицы
    velocity_direction_table.iloc[raw_number - 1] = 0
    raw_index = raw_number - 2
    # делаю таблицу с продолжительностью каждой градации по каждому
    # направлению (таблица 3.3)
    while raw_index != -1:
        velocity_direction_table.iloc[
            raw_index] += velocity_direction_table.iloc[raw_index + 1]
        raw_index -= 1
    # заменяю название строки All на значение скорости ветра, который не
    # наблюдался
    max_observed_wind_velocity = velocity_direction_table.index[raw_number - 2]
    velocity_direction_table_2 = velocity_direction_table.rename(
        {'All': (max_observed_wind_velocity + 1)}, axis='index')
    return velocity_direction_table_2


# вычисляю скорость ветра по значению режимной функции
def linear_interpolation(F, velocity_direction_table, column_number):
    raw_number = 0
    wind_speed = 'error'
    # перебираю сверху вниз каждую строку в одном из столбцов таблицы 3.3
    for f_value in velocity_direction_table.iloc[:, column_number]:
        # если значение режимной функции меньше значения в данной строке, то
        # спускаюсь на 1 строку вниз
        if F < f_value:
            raw_number += 1
            continue
        # если значение режимной функции равно значению в данной строке, то
        # название данной строки - это и есть скорость ветра, которую мы ищем
        elif F == f_value:
            wind_speed = velocity_direction_table.index[raw_number]
            break
        # если значение режимной функции больше значения в данной строке, то
        # нужная нам скорость равна значению, расположенному в интервале между названием
        # данной строки и названием предыдущей строки.
        # вычисляю нужную нам скорость ветра, линейно интерполируя между
        # строками таблицы 3.3
        elif F > f_value:
            # название предыдущей строки
            lower_wind_speed = velocity_direction_table.index[
                raw_number - 1]
            # название данной строки
            bigger_wind_speed = velocity_direction_table.index[raw_number]
            lower_duration = velocity_direction_table.iloc[
                raw_number - 1, column_number]
            bigger_duration = f_value
            # вычисляю угловой коэффициент уравнения прямой
            slope = (lower_wind_speed - bigger_wind_speed) / \
                (lower_duration - bigger_duration)
            # вычисляю показатель ординаты уравнения прямой
            ordinate_coefficient = (lower_duration * bigger_wind_speed -
                                    bigger_duration * lower_wind_speed) / \
                (lower_duration - bigger_duration)
            # подставляю значение режимной функции в уравнение прямой и получаю
            # нужную нам скорость ветра
            wind_speed = slope * F + ordinate_coefficient
            break
    return wind_speed


# вычисляем значение режимной функции F по формуле (3.1) и рассчитываю
# скорость ветра
def speed_calculation(direction_recurrence, velocity_direction_table):
    # продолжительность шторма всегда принимается равной 6 часам
    STORM_DURATION = 6
    # эмпирический коэффициент из формулы (3.1)
    COEF = 4.17
    # число дней в расчётном периоде. Это должно рассчитываться автоматически
    DAYS_NUMBER = 30
    # нормативная повторяемость в годах. Должна задаваться пользователем
    STORM_RECURRENCE = 25
    # рассчитываем F для каждого направления ветра
    wind_speed_list = []
    column_number = 0
    # перебираю каждый столбец таблицы 3.3, то есть каждое направление ветра
    for direction_recurrence in direction_recurrence.loc['All']:
        # рассчитываю значение режимной функции по формуле 3.1
        F = COEF * STORM_DURATION / \
            (DAYS_NUMBER * STORM_RECURRENCE * direction_recurrence * 100)
        # вычисляю скорость ветра по значению режимной функции, линейно
        # интерполируя между строками таблицы 3.3
        wind_velocity = linear_interpolation(
            F, velocity_direction_table, column_number)
        wind_speed_list.append(wind_velocity)
        column_number += 1
    return wind_speed_list


# создаю график режимных скоростей ветра
def figure_plotting(velocity_direction_table):
    # значения функций по оси скоростей
    velocity_axis = velocity_direction_table.index.values
    figure = plt.figure()
    # создаю две пары осей: слева и справа
    left_graphs = figure.add_subplot(1, 2, 1)
    right_graphs = figure.add_subplot(1, 2, 2)
    graph_number = 0
    for direction in velocity_direction_table.columns:
        graph_number += 1
        # значения функций по оси продолжительностей
        duration_axis = velocity_direction_table[direction].values
        # рисую график на левых осях. Если графиков на левых осях становится
        # больше 8, то рисую графики на правых осях
        if graph_number <= 8:
            left_graphs.plot(velocity_axis, duration_axis)
        else:
            right_graphs.plot(velocity_axis, duration_axis)
    # делаю вертикальную ось логарифмической
    left_graphs.set_yscale('symlog', linthreshy=0.001)
    right_graphs.set_yscale('symlog', linthreshy=0.001)
    # вывожу рисочки по вертикальной оси
    y_labels = numpy.geomspace(0.002, 1.024, 9)
    left_graphs.set_yticks(y_labels)
    right_graphs.set_yticks(y_labels)
    # меняю формат подписей
    left_graphs.yaxis.set_major_formatter(tick.ScalarFormatter())
    right_graphs.yaxis.set_major_formatter(tick.ScalarFormatter())   
    # настраиваю максимальные и минимальные значения осей
    MINIMAL_X = 0
    MAXIMAL_X = velocity_axis.max()
    MINIMAL_Y = 0.01
    MAXIMAL_Y = 0.5
    left_graphs.axis([MINIMAL_X, MAXIMAL_X, MAXIMAL_Y, MINIMAL_Y])
    right_graphs.axis([MINIMAL_X, MAXIMAL_X, MAXIMAL_Y, MINIMAL_Y])

    plt.show()

# создаю сводную таблицу
create_pivot_table_result = create_pivot_table()
# обрабатываю штили
PIVOT_TABLE_POSITION = 0
velocity_direction_table = create_pivot_table_result[PIVOT_TABLE_POSITION]
velocity_direction_table = calm_processing(velocity_direction_table)
# делаю таблицу с повторяемостью градаций от общего числа всех наблюдений
# (таблица 3.1)
OBSERVATIONS_NUMBER_POSITION = 1
observations_number = create_pivot_table_result[OBSERVATIONS_NUMBER_POSITION]
direction_recurrence = velocity_direction_table / observations_number
direction_recurrence = direction_recurrence.drop(columns='All')
# делаю таблицу с повторяемостью градаций в каждом румбе (таблица 3.2)
velocity_direction_table = recurrence_per_every_direction(
    velocity_direction_table)
# делаю таблицу с продолжительностью каждой градации по каждому
# направлению (таблица 3.3)
velocity_direction_table = speed_direction_duration(velocity_direction_table)
# эта таблица содержит координаты режимных функций ветра (рисунок 1)
print(velocity_direction_table)
# делаю рисунок режимных функций ветра по каждому направлению (рисунок 1)
figure_plotting(velocity_direction_table)
# рассчитываем значение режимной функции для каждого направления ветра
output = speed_calculation(direction_recurrence, velocity_direction_table)
print(output)
