from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, String, ForeignKey
from db_connection import get_engine


engine = get_engine()
Base = declarative_base()


class WeatherDataEntry(Base):
    __tablename__ = 'baseclass'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    oldest_index = Column(Integer)
    oldest_data = Column(Integer)
    latest_index = Column(Integer)
    latest_data = Column(Integer)


class ProcessedFiles(Base):
    __tablename__ = 'processedfiles'
    id = Column(Integer, primary_key=True)
    filedate = Column(String)

class MaxTempEntry(WeatherDataEntry):
    __tablename__ = 'maxtemp'
    id = Column(Integer, ForeignKey('baseclass.id'), primary_key=True)

class MinTempEntry(WeatherDataEntry):
    __tablename__ = 'mintemp'
    id = Column(Integer, ForeignKey('baseclass.id'), primary_key=True)

class RainfallEntry(WeatherDataEntry):
    __tablename__ = 'rainfall'
    id = Column(Integer, ForeignKey('baseclass.id'), primary_key=True)

class ChanceOfRainEntry(WeatherDataEntry):
    __tablename__ = 'chanceofrain'
    id = Column(Integer, ForeignKey('baseclass.id'), primary_key=True)


if __name__ == '__main__':
    Base.metadata.create_all(engine)
