from random import randrange
import datetime

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from auth import gr_token, login, passwd


gr_session = vk_api.VkApi(token=gr_token)
longpoll = VkLongPoll(gr_session)


def auth_handler():
    # При двухфакторной аутентификации вызывается эта функция.
    key = input("Enter authentication code: ")
    # Если: True - сохранить, False - не сохранять.
    remember_device = True
    return key, remember_device


vk_session = vk_api.VkApi(login, passwd, auth_handler=auth_handler)

# Попытка авторизации
try:
    vk_session.auth()
except vk_api.exceptions.AuthError as error:
    # Обработка ошибки авторизации
    if error.code == 4:  # ошибка двухфакторной аутентификации
        code = input('Введите код двухфакторной аутентификации: ')
        vk_session.auth(code=code)
    else:
        raise error

# Получение ключа доступа от имени пользователя
vk = vk_session.get_api()
access_token = vk_session.token['access_token']


def write_msg(user_id, message):
    gr_session.method('messages.send', {
        'user_id': user_id,
        'message': message,
        'random_id': randrange(10 ** 7),
    })


def get_user_info(user_id):
    # получение данных о пользователе по его id
    vk = gr_session.get_api()
    user_info = vk.users.get(user_ids=user_id, fields='photo_max_orig,city,sex,bdate')
    return user_info[0]


def search_users(user_id):
    current_year = datetime.datetime.now().year
    user_info = get_user_info(user_id)
    vk = vk_session.get_api()
    users = vk.users.search(
        q='',  # Пустой запрос, чтобы получить всех пользователей
        city=user_info['city']['id'],
        age_from=current_year - int(user_info['bdate'].split('.')[2]),
        age_to=current_year - int(user_info['bdate'].split('.')[2]),
        sex=1 if user_info['sex'] == 2 else 2,
        # Противоположный пол (1 - женский, 2 - мужской)
        status=user_info.get('relation', 1)
        # Семейное положение пользователя, если не указан, то ставим 1, то есть не женаты / не замужем
        )

    # Вывод результатов
    for user in users['items']:
        print(user['first_name'], user['last_name'])


def vk_long_poll():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                request = event.text.lower()
                user_id = event.user_id

                if request == "привет":
                    write_msg(user_id, f"Привет, {get_user_info(user_id)['first_name']}")
                elif request == "пока":
                    write_msg(user_id, f"Пока, {get_user_info(user_id)}")
                elif request == "поиск":
                    search_users(user_id)
                else:
                    write_msg(user_id, "Не понял вашего ответа...")
