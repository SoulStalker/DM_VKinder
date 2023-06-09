import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from auth import gr_token, vk_token
from backend import VkBackend
from db_ops import Handling


class VkFront:
    def __init__(self, gr_token, vk_token):
        self.interface = vk_api.VkApi(token=gr_token)
        self.api = VkBackend(vk_token)
        self.params = None
        self.res_users = []

    def create_keyboard(self, one_time=False):
        """
        Клавиатура для общения с пользователем.
        :param one_time: единоразовая или постоянная.
        :return: метод клавитуры для ВК
        """
        keyboard = VkKeyboard(one_time=one_time)
        keyboard.add_button('Старт', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Пока', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Поиск', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Дальше', color=VkKeyboardColor.PRIMARY)

        return keyboard.get_keyboard()

    def write_msg(self, user: int, text: str, url=None, kb=None):
        """
        Отправка сообщения в диалог
        :param user: id пользователя
        :param text: текс сообщения
        :param url: ссылка(ссылки) на вложение
        :param kb: клавиатура
        :return: None
        """
        self.interface.method('messages.send',
                              {'user_id': user,
                               'message': text,
                               'keyboard': kb,
                               'attachment': url,
                               'random_id': get_random_id()
                               }
                              )

    def check_params(self, user_id):
        required_params = ['sex', 'bdate', 'home_town']
        params = self.params
        for param in params:
            if param in required_params:
                if param == 'sex':
                    self.write_msg(user_id, 'Введите ваш пол "мужской" или "женский":')
                    request, user_id = self.vk_long_poll()
                    if request == 'мужской':
                        self.params[param] = 1
                    elif request == 'женский':
                        self.params = 2
                elif param == 'bdate':
                    self.write_msg(user_id, 'Введите дату вашего рождения в формате ДД.ММ.ГГГГ:')
                    request, user_id = self.vk_long_poll()
                    self.params[param] = request
                elif param == 'home_town':
                    self.write_msg(user_id, 'Введите город поиска:')
                    request, user_id = self.vk_long_poll()
                    self.params[param] = request
        return params

    def vk_long_poll(self):
        """
        Метод прослушивания диалога.
        :return: ответ пользователя и его id
        """
        longpoll = VkLongPoll(self.interface)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    request = event.text.lower()
                    return request, event.user_id

    def bot(self):
        """
        Основной метод взаимодействия бота с пользователем.
        :return: None
        """
        while True:
            offset = 0
            request, user_id = self.vk_long_poll()
            self.params = self.api.get_user_info(user_id)
            if request == "привет" or request == "старт":
                keyboard = self.create_keyboard()
                self.write_msg(user=user_id, text=f"Привет, {self.params['name']}", kb=keyboard)
            elif request == "пока":
                keyboard = self.create_keyboard()
                self.write_msg(user=user_id, text=f"Пока, {self.params['name']}", kb=keyboard)
            elif request == "поиск":
                keyboard = self.create_keyboard()

                users = self.api.search_users(self.check_params(user_id=user_id))

                offset += 1

                for user in users:
                    db_handler = Handling(user_id, user['id'], user['photo_url'])
                    if not db_handler.is_person_in_db():
                        self.res_users.append(user)

                self.write_msg(user_id,
                               f'Найдено {len(self.res_users)} пользователей.'
                               f'Нажмите "Дальше" для просмотра следующего пользователя', kb=keyboard)

            elif request == 'дальше':
                keyboard = self.create_keyboard()
                if not self.res_users:
                    self.write_msg(user_id, f'Нажмите "Поиск" для начала поиска', kb=keyboard)
                else:
                    user = self.res_users.pop()
                    db_handler = Handling(user_id, user['id'], user['photo_url'])
                    photos_user = self.api.get_top_photos(user['id'])
                    keyboard = self.create_keyboard(one_time=True)
                    self.write_msg(user_id, f'{user["name"]}\nСсылка на профиль: https://vk.com/id{user["id"]}',
                                   photos_user, kb=keyboard)
                    if not db_handler.is_person_in_db():
                        db_handler.save_search_results()
            else:
                keyboard = self.create_keyboard()
                self.write_msg(user_id, "Неизвестный запрос", kb=keyboard)


if __name__ == '__main__':
    front_api = VkFront(gr_token, vk_token)
    front_api.bot()
