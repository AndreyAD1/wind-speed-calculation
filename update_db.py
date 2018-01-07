import datetime

from database import db_session, Meteostation, Wind
from weather import get_weather


def update_meteostation(station_id, start_date, end_date):
    weather_data = get_weather(station_id, start_date, end_date)
    # ищем метеостанцию в таблице
    station = Meteostation.query.get(station_id)
    if station is None:
        # если не нашли такую станцию, добавляем ее в таблицу
        station = Meteostation(station_id)
        db_session.add(station)
    for row in weather_data:
        localdate = datetime.datetime.strptime(
            row['Localdate'], '%d.%m.%Y %H:%M')
        wind_speed = int(row['U'])
        wind_direction = row['DD']
        # ищем комбо даты и id станции
        wind = Wind.query.get((localdate, station.id))
        if wind is None:
            # если не нашли такое комбо, добавляем в таблицу
            wind = Wind(localdate, wind_speed, wind_direction, station.id)
            db_session.add(wind)
    db_session.commit()


if __name__ == "__main__":
    update_meteostation('27514', '16.12.2017', '18.12.2017')
