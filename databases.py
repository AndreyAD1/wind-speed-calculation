import json
import gzip

from datetime import datetime, timedelta

from sqlalchemy import (
    create_engine, Column, Integer, String, Text,
    DateTime, ForeignKey, func
)
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

from data_capture import get_weather

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

    def __repr__(self):
        return '<{} {} {} {}>'.format(
            self.weather_station_id,
            self.local_date,
            self.wind_speed,
            self.wind_direction
        )


MAX_DAYS = 365


def _make_intervals(start_date, end_date, max_days=MAX_DAYS):
    delta = end_date - start_date
    intervals = []
    if delta.days > max_days:
        start = start_date
        end = start + timedelta(days=max_days)
        while end < end_date:
            intervals.append((start, end))
            start = end
            end = start + timedelta(days=max_days)
        if start < end_date:
            intervals.append((start, end_date))
    else:
        intervals.append((start_date, end_date))
    return intervals


def check_db(station_id, start_date, end_date):
        station = WeatherStation.query.get(station_id)
        if station is not None:
            days_in_period = (end_date - start_date).days
            days_in_db = WindIndicator.query.filter(
                WindIndicator.weather_station_id == station_id,
                WindIndicator.local_date <= end_date,
                WindIndicator.local_date >= start_date
            ).group_by(
                func.strftime("%Y-%m-%d", WindIndicator.local_date)
            ).count()
            if days_in_period == days_in_db:
                return
        else:
            station = WeatherStation(id=station_id)
            db_session.add(station)

        intervals = _make_intervals(start_date, end_date)
        for start, end in intervals:
            weather_data = get_weather(station_id, start, end)
            for row in weather_data:
                local_date = datetime.strptime(
                    row['Localdate'], '%d.%m.%Y %H:%M')
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
                        weather_station_id=station.id)
                    db_session.add(wind)
            db_session.commit()


def create_db():
    Base.metadata.create_all(bind=engine)


def load_wmo():
    with gzip.open('wmo.json.gz') as f:
        data = json.load(f)
    for row in data:
        station = WeatherStation(id=row['id'], name=row['name'])
        db_session.add(station)
    db_session.commit()


if __name__ == "__main__":
    create_db()
    load_wmo()
