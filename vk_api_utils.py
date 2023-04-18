from random import randrange
import datetime

import vk_api
import requests
from vk_api.longpoll import VkLongPoll, VkEventType
from auth import gr_token, login, passwd


gr_session = vk_api.VkApi(token=gr_token)
longpoll = VkLongPoll(gr_session)


def auth_handler():
    # При двухфакторной аутентификации вызывается эта функция.
    key = input("Enter authentication code: ")
    remember_device = True
    return key, remember_device


vk_session = vk_api.VkApi(login, passwd, auth_handler=auth_handler)

# Попытка авторизации
try:
    vk_session.auth()
except vk_api.exceptions.AuthError as error:
    # Обработка ошибки авторизации
    if error.code == 4:
        code = input('Введите код двухфакторной аутентификации: ')
        vk_session.auth(code=code)
    else:
        raise error

# Получение ключа доступа от имени пользователя
vk = vk_session.get_api()
access_token = vk_session.token['access_token']


def write_msg(user_id, message, attachment=None):
    if attachment:
        attachment = ', '.join(attachment)
    gr_session.method('messages.send', {
        'user_id': user_id,
        'message': message,
        'attachment': attachment,
        'random_id': randrange(10 ** 7)
    })


def get_user_info(user_id):
    # получение данных о пользователе по его id
    vk = gr_session.get_api()
    user_info = vk.users.get(user_ids=user_id, fields='photo_max_orig,city,sex,bdate')
    return user_info[0]


def get_top_photos(user_id):
    vk = vk_session.get_api()
    gr = gr_session.get_api()
    # Проверяем, является ли профиль пользователя приватным
    user_info = vk.users.get(user_ids=user_id, fields='is_closed')[0]
    if user_info['is_closed']:
        return f"Профиль пользователя {user_id} является приватным"

    # Получаем информацию о пользователе
    user_info = vk.users.get(user_ids=user_id, fields='photo_max_orig')[0]
    # Получаем список фотографий пользователя
    photos = vk.photos.get(owner_id=user_id, album_id='profile', extended=1, count=100)
    # Сортируем фотографии по количеству лайков
    sorted_photos = sorted(photos['items'], key=lambda x: x['likes']['count'], reverse=True)
    # Получаем топ-3 фотографии
    top_photos = sorted_photos[:3]
    # Отправляем фотографии и ссылку на пользователя в чат
    message = f"Топ-3 популярных фотографии профиля {user_info['first_name']} {user_info['last_name']}: \n"
    attachment = []
    for top_photo in top_photos:
        photo_url = top_photo['sizes'][-1]['url']
        photo_data = requests.get(photo_url).content
        upload_url = vk.photos.getMessagesUploadServer()['upload_url']
        response = requests.post(upload_url, files={'photo': ('photo.jpg', photo_data)})
        result = response.json()
        # Сохранение фотографии на сервере ВКонтакте
        photo = vk.photos.saveMessagesPhoto(server=result['server'], photo=result['photo'], hash=result['hash'])[0]
        message += f"{top_photo['sizes'][-1]['url']} \n"
        attachment.append(f'photo{photo["owner_id"]}_{photo["id"]}')
    message += f"Ссылка на профиль: https://vk.com/id{user_id} \n"
    return message, attachment


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
    for user in users['items']:
        receive_data = get_top_photos(user['id'])
        write_msg(user_id, receive_data[0], receive_data[1])


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
