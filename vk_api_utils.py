from random import randrange
import datetime

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from auth import gr_token, login, passwd
from db_ops import Handling


class VkBot:
    def __init__(self):
        self.gr_session = vk_api.VkApi(token=gr_token)
        self.longpoll = VkLongPoll(self.gr_session)
        self.gr = self.gr_session.get_api()
        self.buttons = [
            {'label': 'Кнопка 1', 'color': VkKeyboardColor.PRIMARY},
            {'label': 'Кнопка 2', 'color': VkKeyboardColor.PRIMARY}
        ]
        self.kb = self.create_keyboard(buttons=self.buttons
                                       )

    def create_keyboard(self, buttons, one_time=False):
        keyboard = VkKeyboard(one_time=one_time)
        for button in buttons:
            keyboard.add_button(button['label'], color=buttons['color'])
        return keyboard.get_keyboard()

    def write_msg(self, user: int, text: str, url=None):
        # функция отправки сообщения
        gr.messages.send(
            user_id=user,
            message=text,
            keybard=self.kb(),
            attachment=url,
            random_id=randrange(10 ** 7)
        )


gr_session = vk_api.VkApi(token=gr_token)
gr = gr_session.get_api()
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
except vk_api.exceptions.Captcha as captcha:
    # это помогло мне избегать ошибки капчи
    captcha.sid
    captcha.get_url()
    captcha.get_image()

vk = vk_session.get_api()
access_token = vk_session.token['access_token']


# def send_photo(id, url):
#     # функция отправки фото
#     gr.messages.send(
#         user_id=id,
#         attachment=url,
#         random_id=randrange(10 ** 7)
#     )


def get_user_info(user_id):
    # получение данных о пользователе по его id
    vk = gr_session.get_api()
    user_info = vk.users.get(user_ids=user_id, fields='photo_max_orig,city,sex,bdate')
    return user_info[0]


def get_top_photos(user_id):
    vk = vk_session.get_api()
    # gr = gr_session.get_api()
    # # Получаем информацию о пользователе
    # user_info = vk.users.get(user_ids=user_id, fields='photo_max_orig')[0]
    # Получение списка фотографий пользователя
    photos = vk.photos.get(owner_id=user_id, album_id='profile', extended=1)
    # Сортировка списка фотографий по количеству лайков
    sorted_photos = sorted(photos['items'], key=lambda x: x['likes']['count'], reverse=True)
    # Получение ссылок на три популярных фотографии
    top_photos = sorted_photos[:3]
    photo_links = [f"photo{p['owner_id']}_{p['id']}" for p in top_photos]
    attachment = ",".join(photo_links)
    message = f"Ссылка на профиль: https://vk.com/id{user_id} \n"
    return message, attachment


def search_users(user_id):
    current_year = datetime.datetime.now().year
    user_info = get_user_info(user_id)
    vk = vk_session.get_api()
    users = vk.users.search(
        q='',
        # Пустой запрос, чтобы получить всех пользователей
        city=user_info['city']['id'],
        age_from=current_year - int(user_info['bdate'].split('.')[2]),
        age_to=current_year - int(user_info['bdate'].split('.')[2]),
        sex=1 if user_info['sex'] == 2 else 2,
        # Противоположный пол (1 - женский, 2 - мужской)
        status=user_info.get('relation', 1)
        # Семейное положение пользователя, если не указан, то ставим 1, то есть не женаты / не замужем
    )
    for user in users['items']:
        # если профиль не закрыт
        if not user['is_closed']:
            receive_data = get_top_photos(user['id'])
            search_results = {'person_id': int(user['id']), 'photo_url': receive_data[1]}
            # проверяем нет ли человека в базе
            handler = Handling(user_id, search_results['person_id'], search_results['photo_url'])
            if not handler.is_person_in_db():
                # сохраняем запись
                handler.save_search_results()
                # возвращаем ссылку на профиль и фотки
                VkBot.write_msg(user_id, receive_data[0], receive_data[1])
                # send_photo(user_id, receive_data[1])


def vk_long_poll():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                request = event.text.lower()
                user_id = event.user_id
                if request == "привет" or request == "start":
                    # keyboard = VkKeyboard()
                    # keyboard.add_button("Поиск", color=VkKeyboardColor.NEGATIVE)
                    # keyboard.add_line()
                    VkBot.write_msg(user=user_id, text=f"Привет, {get_user_info(user_id)['first_name']}")
                elif request == "пока":
                    VkBot.write_msg(user=user_id, text=f"Пока, {get_user_info(user_id)}")
                elif request == "поиск":
                    search_users(user_id)
                else:
                    VkBot.write_msg(user_id, "Не понял вашего ответа...")
