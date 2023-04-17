# модуль, содержащий класс Handling и методы для работы с базой данных.
# Handling - класс для работы с базой данных, содержащий методы для сохранения
# результатов поиска, добавления людей в избранный и черный списки,
# а также методы для проверки наличия человека в базе данных перед поиском.
from sqlalchemy.orm import DeclarativeMeta

from database import db
from models import SearchResults

# class Handling():
#     def __init__(self, db_name):
#         pass
# def close(self):
    #     self.conn.close()


def insert_data(db: db, model: DeclarativeMeta, kw_data: dict):
    new_data = model(**kw_data)
    db.add(new_data)
    db.commit()


def save_search_results(user_id, search_results):
    # сохранение данных о результатах поиска в базу
    for result in search_results:
        data = {
            'user_id': user_id,
            'person_id': result['person_id'],
            'photo_url': result['photo_url'],
            'likes': result['likes'],
            'comments': result['comments']
        }
        insert_data(db, SearchResults, data)

    # def add_to_favorites(self, user_id, person_id):
    #     self.cursor.execute('INSERT INTO favorites VALUES (%s, %s)', (user_id, person_id))
    #     self.conn.commit()
    #
    # def add_to_blacklist(self, user_id, person_id):
    #     self.cursor.execute('INSERT INTO blacklist VALUES (%s, %s)', (user_id, person_id))
    #     self.conn.commit()
    #
    # def is_person_in_database(self, person_id):
    #     self.cursor.execute('SELECT * FROM search_results WHERE person_id = %s', (person_id,))
    #     return self.cursor.fetchone() is not None
    #

