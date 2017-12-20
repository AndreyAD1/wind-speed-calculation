
import re
import io
import codecs
import csv
import gzip
import datetime

import requests


URL = 'https://rp5.ru/responses/reFileSynop.php'


HEADERS = {
    'Accept': 'text/html, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-GB,en;q=0.9,en-US;q=0.8,ru;q=0.7',
    'Content-type': 'application/x-www-form-urlencoded',
    'Referer': 'https://rp5.ru/',
    'User-Agent':
              'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2)'
              'AppleWebKit/537.36 (KHTML, like Gecko)'
              'Chrome/63.0.3239.84 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}


class RP5FormatError(BaseException):
    pass


def handle_date(date):
    if isinstance(date, str):
        return date
    elif isinstance(date, datetime.date):
        return date.strftime('%d.%m.%Y')
    else:
        raise ValueError('Date must be datetime.date or str')


def get(station_id,
        start_date, end_date,
        month=None):
    '''
    station_id: str | int - id метеостанции
    start_date: datetime.date | str (DD.MM.YYYY) - начало периода
    end_date: datetime.date | str (DD.MM.YYYY) - конец периода
    month: int - порядковый номер месяца (начиная с 1)

    Если параметр month задан, то результатом будут данные за месяц,
    если не задан - за все дни в периоде
    '''
    if month is None:
        report_type = '1'
    else:
        if isinstance(month, int):
            report_type = '2'
        else:
            raise ValueError('Month argument must be int')

    form_data = {
        'wmo_id': station_id,
        'a_date1': handle_date(start_date),
        'a_date2': handle_date(end_date),
        'f_ed3': month,
        'f_pe': report_type,
        'f_pe1': '2',
        'lng_id': '2'
    }

    # Запрос ссылки на датасет с заданными параметрами
    response = requests.post(URL, data=form_data, headers=HEADERS)
    href = re.findall('http.*gz', response.text)
    if len(href) == 0:
        raise RP5FormatError
    url = href[0].split('/')
    url = '/'.join([part for part in url if part != '..'])

    # Загрузка датасета по ссылке
    response = requests.get(url)

    # Декомпрессия
    compressed_data = response.content
    decompressed_data = gzip.decompress(compressed_data)
    byte_io = io.BytesIO(decompressed_data)
    string_io = codecs.iterdecode(byte_io, "utf-8")
    filtered_io = filter(lambda row: row[0] != '#', string_io)

    # Чтение CSV-файла и формирование результата
    reader = csv.DictReader(filtered_io, delimiter=';', quotechar='"')
    data = []
    for row in reader:
        row = dict(row)
        if None in row:
            del row[None]
        first_field = reader.fieldnames[0]
        row['localdate'] = row[first_field]
        del row[first_field]
        data.append(row)

    return data


if __name__ == "__main__":
    weather_data = get('27612', '16.12.2017', '18.12.2017')
    print(weather_data)
