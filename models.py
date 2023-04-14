from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base
from database import db_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    vk_id = Column(Integer, unique=True)
    last_name = Column(String)
    age = Column(Integer)
    sex = Column(Integer)
    city = Column(String)
    status = Column(String)
    found = Column(Boolean, default=False)
    favorite = Column(Boolean, default=False)
    blacklisted = Column(Boolean, default=False)


class Photo(Base):
    __tablename__ = 'photos'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    photo_id = Column(String)
    likes = Column(Integer)
    comments = Column(Integer)


def create_db():
    Base.metadata.drop_all(db_engine)
    Base.metadata.create_all(db_engine)


if __name__ == '__main__':
    create_db()
