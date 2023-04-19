from sqlalchemy.orm import DeclarativeMeta

from database import db
from models import Persons, Favorites, Blacklist


class Handling:
    def __init__(self, user_id, person_id, photo_url):
        self.user_id = user_id
        self.person_id = person_id
        self.photo_url = photo_url

    def save_search_results(self):
        # сохранение данных о результатах поиска в базу
        data = {
            'user_id': self.user_id,
            'person_id': self.person_id,
            'photo_url': self.photo_url
        }
        insert_data(db, Persons, data)

    def is_person_in_db(self):
        # проверка наличия записи в базе
        return db.query(Persons).filter_by(
            user_id=self.user_id,
            person_id=self.person_id
        ).first() is not None

    def add_to_favorites(self):
        # добавление в избранное
        data = {'user_id': self.user_id, 'person_id': self.person_id}
        insert_data(db, Favorites, data)

    def add_to_blacklist(self):
        # добавление в черный список
        data = {'user_id': self.user_id, 'person_id': self.person_id}
        insert_data(db, Blacklist, data)


def insert_data(data_base: db, model: DeclarativeMeta, kw_data: dict):
    # функция вставки данных в базу
    new_data = model(**kw_data)
    data_base.add(new_data)
    data_base.commit()



