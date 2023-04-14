from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def create_session(db_url):
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    return Session(), engine


with open('dsn.txt', encoding='utf-8') as dsn_file:
    # строка подключения к базе
    dsn = dsn_file.read()

db, db_engine = create_session(dsn)

