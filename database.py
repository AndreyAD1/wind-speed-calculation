#! /usr/bin/env python
# Зачем здесь это? Вы планируете использовать второй питон? Он через 2 года перестает поддерживаться
# https://pythonclock.org/
# -*- coding: utf-8 -*-

# from sqlalchemy import create_engine, Column, Integer, String, Text, \
#     DateTime, ForeignKey
# Чище сделать вот так
from sqlalchemy import (
    create_engine, Column, Integer, String, Text,
    DateTime, ForeignKey
)
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///wind.db')
db_session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


# class Meteostation(Base):
# Лучше использовать английские слова в названиях классов, мне PyCharm здесь показывает ошибку, т.к. не знает
# слова Meteostation
class WeatherStation(Base):
    __tablename__ = 'weather_stations'
    # Почему id строка?
    id = Column(String(), primary_key=True)
    winds = relationship('Wind', backref='weather_station')

    # Зачем это?
    def __init__(self, id=None):
        self.id = id


# Не совсем понятное название класса
class Wind(Base):
    __tablename__ = 'wind'
    # localdate = Column(DateTime, primary_key=True)
    # Опять PyCharm подсветил ошибку, т.к. не знает английского слова localdate
    # Хорошо бы и для этой таблицы добавить поле id
    local_date = Column(DateTime, primary_key=True)
    wind_speed = Column(Integer, nullable=False)
    wind_direction = Column(Text)
    weather_station_id = Column(
        String(),
        ForeignKey('weather_stations.id'),
        primary_key=True
    )

    # Зачем это?
    def __init__(self,
                 localdate=None, wind_speed=None,
                 wind_direction=None, meteo_id=None):
        self.localdate = localdate
        self.wind_speed = wind_speed
        self.wind_direction = wind_direction
        self.meteo_id = meteo_id


if __name__ == "__main__":
    # Явнее будет вынести это в какую-то отдельную функцию, например create_database
    Base.metadata.create_all(bind=engine)
