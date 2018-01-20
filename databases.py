import datetime

from sqlalchemy import (
    create_engine, Column, Integer, String, Text,
    DateTime, ForeignKey
)
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

from weather import get_weather

engine = create_engine('sqlite:///wind.db')
db_session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


class WeatherStation(Base):
    __tablename__ = 'weather_stations'
    id = Column(String(), primary_key=True)
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


def load_weather_data(station_id, start_date, end_date):
    weather_data = get_weather(station_id, start_date, end_date)
    station = WeatherStation.query.get(station_id)
    if station is None:
        station = WeatherStation(id=station_id)
        db_session.add(station)
    for row in weather_data:
        local_date = datetime.datetime.strptime(
            row['Localdate'], '%d.%m.%Y %H:%M')
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


if __name__ == "__main__":
    create_db()
    load_weather_data('27514', '16.12.2017', '18.12.2017')
