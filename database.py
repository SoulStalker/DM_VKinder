from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from auth import dsn


def create_session(db_url):
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    return Session(), engine


db, db_engine = create_session(dsn)

