from flask_login import UserMixin
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base, UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(255))
    password_hash = Column(String(255))


if __name__ == '__main__':
    from scraper.db_connection import get_engine
    engine = get_engine()
    Base.metadata.create_all(engine)