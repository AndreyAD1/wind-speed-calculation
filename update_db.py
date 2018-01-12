import datetime

from database import db_session, WeatherStation, WindIndicator
from weather import get_weather


def update_meteostation(station_id, start_date, end_date):
    weather_data = get_weather(station_id, start_date, end_date)
    # ищем метеостанцию в таблице
    station = WeatherStation.query.get(station_id)
    if station is None:
        # если не нашли такую станцию, добавляем ее в таблицу
        station = WeatherStation(station_id)
        db_session.add(station)
    for row in weather_data:
        local_date = datetime.datetime.strptime(
            row['Localdate'], '%d.%m.%Y %H:%M')
        wind_speed = int(row['U'])
        wind_direction = row['DD']
        # ищем комбо даты и id станции
        wind = WindIndicator.query.get((local_date, station.id))
        if wind is None:
            # если не нашли такое комбо, добавляем в таблицу
            wind = WindIndicator(
                local_date, wind_speed, wind_direction, station.id)
            db_session.add(wind)
    db_session.commit()


if __name__ == "__main__":
    update_meteostation('27514', '16.12.2017', '18.12.2017')
