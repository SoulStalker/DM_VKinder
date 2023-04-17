from random import randrange

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

# class VkApiClient:


with open('vktoken.txt', encoding='utf-8') as vk_file:
    # токен ВК из файла
    token = vk_file.read()

vk_session = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk_session)


def write_msg(user_id, message):
    vk_session.method('messages.send', {
        'user_id': user_id,
        'message': message,
        'random_id': randrange(10 ** 7),
    })


def get_user_info(user_id):
    #получение данных о пользователе по его id
    vk = vk_session.get_api()
    user_info = vk.users.get(user_ids=user_id, fields='photo_max_orig,city,sex,bdate')
    return user_info[0]['first_name']


def search_users():
    params = {
        'sex': 1,  # пол (1 - женский, 2 - мужской)
        'age_from': 18,  # возраст от
        'age_to': 30,  # возраст до
        'city': 1,  # город (1 - Москва)
        'status': 1  # семейное положение (1 - не женат/не замужем)
    }

    # Поиск пользователей
    vk = vk_session.get_api()
    users = vk.users.search(**params)

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
                    write_msg(user_id, f"Привет, {get_user_info(user_id)}")
                elif request == "пока":
                    write_msg(user_id, f"Пока, {get_user_info(user_id)}")
                elif request == "поиск":
                    search_users()
                else:
                    write_msg(user_id, "Не понял вашего ответа...")
