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
    from scraper.db_connection import get_engine, get_session
    from werkzeug.security import generate_password_hash
    print("Creating user table...")
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("Creating new user...")
    session = get_session()
    u = User()
    username = input("Enter a username: ")
    password = input("Enter a password: ")
    u.username = username
    u.password_hash = generate_password_hash(password)
    session.add(u)
    session.commit()
    print("User added to database.")
