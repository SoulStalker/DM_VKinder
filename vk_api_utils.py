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

    def create_keyboard(self, one_time=False):
        keyboard = VkKeyboard(one_time=one_time)
        keyboard.add_button('Старт', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Пока', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Поиск', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Дальше', color=VkKeyboardColor.PRIMARY)
        return keyboard.get_keyboard()

    def write_msg(self, user: int, text: str, url=None, kb=None):
        self.interface.method('messages.send',
                              {'user_id': user,
                               'message': text,
                               'keyboard': kb,
                               'attachment': url,
                               'random_id': get_random_id()
                               }
                              )

    def vk_long_poll(self):
        longpoll = VkLongPoll(self.interface)
        offset = 0
        res_users = []

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    request = event.text.lower()
                    user_id = event.user_id
                    self.params = self.api.get_user_info(user_id)
                    if request == "привет" or request == "старт":
                        keyboard = self.create_keyboard()
                        self.write_msg(user=user_id, text=f"Привет, {self.params['name']}", kb=keyboard)
                    elif request == "пока":
                        keyboard = self.create_keyboard()
                        self.write_msg(user=user_id, text=f"Пока, {self.params['name']}", kb=keyboard)
                    elif request == "поиск":
                        keyboard = self.create_keyboard()
                        self.write_msg(user_id,
                                       f'Найдено {len(res_users)} пользователей.Нажмите "Дальше" для просмотра следующего пользователя', kb=keyboard)
                        users = self.api.search_users(self.params)
                        for user in users:
                            db_handler = Handling(user_id, user['id'], user['photo_url'])
                            if not db_handler.is_person_in_db():
                                res_users.append(user)
                    elif request == 'дальше' and res_users:
                        user = res_users.pop(0)
                        db_handler = Handling(user_id, user['id'], user['photo_url'])
                        photos_user = self.api.get_top_photos(user['id'])
                        keyboard = self.create_keyboard(one_time=True)
                        self.write_msg(user_id, f'{user["name"]}nСсылка на профиль: https://vk.com/id{user["id"]}',
                                       photos_user, kb=keyboard)
                        db_handler.save_search_results()
                        # offset += 1
                    else:
                        keyboard = self.create_keyboard()
                        self.write_msg(user_id, "Неизвестный запрос", kb=keyboard)


if __name__ == '__main__':
    front_api = VkFront(gr_token, vk_token)
    front_api.vk_long_poll()
