# модуль, содержащий класс Handling и методы для работы с базой данных.
# Handling - класс для работы с базой данных, содержащий методы для сохранения
# результатов поиска, добавления людей в избранный и черный списки,
# а также методы для проверки наличия человека в базе данных перед поиском.
from sqlalchemy.orm import DeclarativeMeta

from database import db
from models import Persons, Favorites, Blacklist


def insert_data(data_base: db, model: DeclarativeMeta, kw_data: dict):
    # функция вставки данных в базу
    new_data = model(**kw_data)
    data_base.add(new_data)
    data_base.commit()


def save_search_results(user_id, search_results):
    # сохранение данных о результатах поиска в базу
    data = {
        'user_id': user_id,
        'person_id': search_results['person_id'],
        'photo_url': search_results['photo_url']
    }
    insert_data(db, Persons, data)


def is_person_in_db(user, person):
    # проверка наличия записи в базе
    return db.query(Persons).filter_by(user_id=user, person_id=person).first() is not None


def add_to_favorites(user, person):
    # добавление в избранное
    data = {'user_id': user, 'person_id': person}
    insert_data(db, Favorites, data)


def add_to_blaklist(user, person):
    # добавление в черный список
    data = {'user_id': user, 'person_id': person}
    insert_data(db, Blacklist, data)
