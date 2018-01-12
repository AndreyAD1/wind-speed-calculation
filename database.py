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


class WeatherStation(Base):
    __tablename__ = 'weather_stations'
    # Почему id строка?
    # В качестве id тут - идентификатор метеостанции, и нет уверенности
    # что это всегда int, а не комбо чисел и букв, например
    id = Column(String(), primary_key=True)
    winds = relationship('WindIndicator', backref='weather_station')

    # конструктор класса WeatherStation
    def __init__(self, id):
        self.id = id


class WindIndicator(Base):
    __tablename__ = 'wind_indicators'
    # Хорошо бы и для этой таблицы добавить поле id
    # не вижу смысла в синтетическом ключе,
    # т.к. PK тут - комбинация local_date и weather_station_id
    local_date = Column(DateTime, primary_key=True)
    wind_speed = Column(Integer, nullable=False)
    wind_direction = Column(Text)
    weather_station_id = Column(
        String(),
        ForeignKey('weather_stations.id'),
        primary_key=True
    )

    # конструктор класса WindIndicators
    def __init__(self,
                 local_date, wind_speed,
                 wind_direction, weather_station_id):
        self.local_date = local_date
        self.wind_speed = wind_speed
        self.wind_direction = wind_direction
        self.weather_station_id = weather_station_id


def create_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_db()
