from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from database import db_engine

Base = declarative_base()


class Persons(Base):
    __tablename__ = 'persons'

    user_id = Column(Integer, primary_key=True)
    person_id = Column(Integer, primary_key=True)
    photo_url = Column(String)


class Favorites(Base):
    __tablename__ = 'favorites'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    person_id = Column(Integer)


class Blacklist(Base):
    __tablename__ = 'blacklist'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    person_id = Column(Integer)


def create_db():
    Base.metadata.drop_all(db_engine)
    Base.metadata.create_all(db_engine)


if __name__ == '__main__':
    create_db()
