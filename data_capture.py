import re
import io
import codecs
import csv
import gzip
import datetime

import requests

from constants import URL, HEADERS, all_days, only_month
from exceptions import *


def _handle_date(date):
    if isinstance(date, str):
        return date
    elif isinstance(date, datetime.date):
        return date.strftime('%d.%m.%Y')
    else:
        raise ValueError('Date must be datetime.date or str')


def _post(url, form_data):
    # Запрос ссылки на датасет с заданными параметрами
    response = requests.post(url, data=form_data, headers=HEADERS)
    print(url)
    print(response)
    href = re.findall('http.*gz', response.text)
    print(href)
    if len(href) == 0:
        raise RP5FormatError
    url = href[0].split('/')
    url = '/'.join(part for part in url if part != '..')
    return url


def _decompress(content):
    decompressed_data = gzip.decompress(content)
    byte_io = io.BytesIO(decompressed_data)
    string_io = codecs.iterdecode(byte_io, "utf-8")
    # filter comments
    filtered_io = [row for row in string_io if len(row) > 0 and row[0] != "#"]
    # filtered_io = filter(lambda row: row[0] != '#', string_io)
    return filtered_io


def get_weather(station_id, start_date, end_date, month=None):
    """
    station_id: str | int - id метеостанции
    start_date: datetime.date | str (DD.MM.YYYY) - начало периода
    end_date: datetime.date | str (DD.MM.YYYY) - конец периода
    month: int - порядковый номер месяца (начиная с 1)

    Если параметр month задан, то результатом будут данные за месяц,
    если не задан - за все дни в периоде
    """
    if not month:
        report_type = all_days
    elif isinstance(month, int):
        report_type = only_month
    else:
        raise ValueError('Month argument must be int')
    """
    'f_pe1': '2' - формат данных - если CSV: 1- Ansi, 2 - UTF-8, 3 - Unicode,
    если XLS - 2 и добавляется новый параметр 'type': 'xls'.
    Так как в проекте используется формат CSV в кодировке UTF-8,
    параметру f_pe1 присвоено неизменяемое значение '2'
    'lng_id': '2' - неизменяемый параметр
    """
    form_data = {
        'wmo_id': station_id,
        'a_date1': _handle_date(start_date),
        'a_date2': _handle_date(end_date),
        'f_ed3': month,
        'f_pe': report_type,
        'f_pe1': '2',
        'lng_id': '2'
    }

    # Запрос ссылки на датасет с заданными параметрами
    url = _post(URL, form_data)

    # Загрузка датасета по ссылке
    response = requests.get(url)

    filtered_io = _decompress(response.content)

    # Чтение CSV-файла и формирование результата
    reader = csv.DictReader(filtered_io, delimiter=';', quotechar='"')
    data = []
    for row in reader:
        if None in row:
            del row[None]
        first_field = reader.fieldnames[0]
        row['Localdate'] = row[first_field]
        del row[first_field]
        data.append(row)

    return data


if __name__ == "__main__":
    weather_data = get_weather('27612', '16.12.2017', '18.12.2017')
    print(weather_data[:100])
