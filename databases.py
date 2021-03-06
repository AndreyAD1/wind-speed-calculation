import json
from datetime import datetime, timedelta
from sqlalchemy import (
    create_engine, Column, Integer, String, Text,
    DateTime, ForeignKey, func
)
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from data_capture import get_weather
from constants import MAX_DAYS

engine = create_engine('sqlite:///wind.db')
db_session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


class WeatherStation(Base):
    __tablename__ = 'weather_stations'
    id = Column(String(), primary_key=True)
    name = Column(Text())
    winds = relationship('WindIndicator', backref='weather_station')

    def __repr__(self):
        return '<Weather station {}>'.format(self.id)


class WindIndicator(Base):
    __tablename__ = 'wind_indicators'
    local_date = Column(DateTime, primary_key=True)
    wind_speed = Column(Integer, nullable=False)
    wind_direction = Column(Text)
    weather_station_id = Column(
        String(),
        ForeignKey('weather_stations.id'),
        primary_key=True
    )
    month = Column(Integer)

    def __repr__(self):
        return '<{} {} {} {} {}>'.format(
            self.weather_station_id,
            self.local_date,
            self.wind_speed,
            self.wind_direction,
            self.month
        )


def _get_intervals(start_date, end_date):
    period_start = start_date
    period_end = period_start + timedelta(days=MAX_DAYS)
    while period_end < end_date:
        yield (period_start, period_end)
        period_start = period_end
        period_end = period_start + timedelta(days=MAX_DAYS)
    yield (period_start, end_date)


def get_data(station_id, start_date, end_date):
    station = WeatherStation.query.get(station_id)
    if station is not None:
        days_in_period = (end_date - start_date).days + 1
        days_in_db = WindIndicator.query.filter(
            WindIndicator.weather_station_id == station_id,
            WindIndicator.local_date <= end_date,
            WindIndicator.local_date >= start_date
        ).group_by(
            func.strftime("%Y-%m-%d", WindIndicator.local_date)
        ).count()
        if days_in_period == days_in_db:
            return

    for start, end in _get_intervals(start_date, end_date):
        print('Send request to rp5.ru')
        weather_data = get_weather(station_id, start, end)
        if station is None:
            station = WeatherStation(id=station_id)
            db_session.add(station)

        for row in weather_data:
            local_date = datetime.strptime(
                row['Localdate'], '%d.%m.%Y %H:%M')
            local_month = local_date.month
            if row['Ff'] == '' or row['DD'] == '':
                continue
            wind_speed = int(row['Ff'])
            wind_direction = row['DD']
            wind = WindIndicator.query.get((local_date, station.id))
            if wind is None:
                wind = WindIndicator(
                    local_date=local_date,
                    wind_speed=wind_speed,
                    wind_direction=wind_direction,
                    weather_station_id=station.id,
                    month=local_month)
                db_session.add(wind)
        try:
            db_session.commit()
        except Exception:
            db_session.rollback()

def create_db():
    Base.metadata.create_all(bind=engine)


def load_wmo():
    with open('wmo_filtered.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    for row in data:
        station = WeatherStation(id=row['id'], name=row['name'])
        db_session.add(station)
    db_session.commit()


if __name__ == "__main__":
    create_db()
    load_wmo()
