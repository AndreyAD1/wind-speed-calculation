# Андрей Аракельянц. 19.12.2017
# Задача этой программы - по данным наблюдений с сайта rp5.ru рассчитать
# скорость ветра заданной обеспеченности по каждому румбу.

from pandas import *
import numpy
from scipy import interpolate


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
    return velocity_direction_table


def F_calculation(direction_recurrence, velocity_direction_table):
    # вычисляем значение режимной функции F из формулы (3.1)
    # продолжительность шторма всегда принимается равной 6 часам
    STORM_DURATION = 6
    # эмпирический коэффициент из формулы (3.1)
    COEF = 4.17
    # число дней в расчётном периоде. Это должно рассчитываться автоматически
    DAYS_NUMBER = 30
    # нормативная повторяемость в годах. Должна задаваться пользователем
    STORM_RECURRENCE = 25
    # рассчитываем F для каждого направления ветра
    output = []
    column_number = 0
    print(velocity_direction_table.iloc[:, column_number])
    for direction_recurrence in direction_recurrence.loc['All']:
        F = COEF * STORM_DURATION / \
            (DAYS_NUMBER * STORM_RECURRENCE * direction_recurrence * 100)
        # for f_value in velocity_direction_table.iloc[:, column_number]:
        #     if F<f_value:
        #         continue
        #     elif F=f:
        #         wind_speed = 
        output.append(F)
    return output


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
# делаю таблицу с повторяемостью градаций в каждом румбе (таблица 3.2)
for column in velocity_direction_table.columns:
    cases_with_this_direction = velocity_direction_table.loc[
        'All', column]  # количество случаев с этим направлением ветра
    velocity_direction_table[
        column] = velocity_direction_table[column] / cases_with_this_direction

# удаляю столбец "All", потому что он не нужен
velocity_direction_table = velocity_direction_table.drop(columns='All')

# делаю таблицу с продолжительностью каждой градации по каждому
# направлению (таблица 3.3)
velocity_direction_table = speed_direction_duration(velocity_direction_table)
# эта таблица сожержит координаты режимных функций ветра (рисунок 1)
print(velocity_direction_table)
# рассчитываем значение режимной функции для каждого направления ветра
output = F_calculation(direction_recurrence, velocity_direction_table)
print(output)
