#! /usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine, Column, Integer, String, Text, \
    DateTime, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///wind.db')
db_session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


class Meteostation(Base):
    __tablename__ = 'meteostations'
    id = Column(String(), primary_key=True)
    winds = relationship('Wind', backref='meteostation')

    def __init__(self, id=None):
        self.id = id


class Wind(Base):
    __tablename__ = 'wind'
    localdate = Column(DateTime, primary_key=True)
    wind_speed = Column(Integer, nullable=False)
    wind_direction = Column(Text)
    meteo_id = Column(
        String(),
        ForeignKey('meteostations.id'),
        primary_key=True
    )

    def __init__(self,
                 localdate=None, wind_speed=None,
                 wind_direction=None, meteo_id=None):
        self.localdate = localdate
        self.wind_speed = wind_speed
        self.wind_direction = wind_direction
        self.meteo_id = meteo_id


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
