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
        # self.buttons = [
        #     {'label': 'Кнопка 1', 'color': VkKeyboardColor.PRIMARY},
        #     {'label': 'Кнопка 2', 'color': VkKeyboardColor.PRIMARY}
        # ]
        # self.kb = self.create_keyboard(buttons=self.buttons
        #                                )

    #
    # def create_keyboard(self, buttons, one_time=False):
    #     keyboard = VkKeyboard(one_time=one_time)
    #     for button in buttons:
    #         keyboard.add_button(button['label'], color=buttons['color'])
    #     return keyboard.get_keyboard()

    def write_msg(self, user: int, text: str, url=None):
        self.interface.method('messages.send',
                              {'user_id': user,
                               'message': text,
                               # keybard=self.kb(),
                               'attachment': url,
                               'random_id': get_random_id()
                               }
                              )

    def vk_long_poll(self):
        longpoll = VkLongPoll(self.interface)
        users = []

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    request = event.text.lower()
                    user_id = event.user_id
                    self.params = self.api.get_user_info(user_id)

                    if request == "привет" or request == "start":
                        self.write_msg(user=user_id, text=f"Привет, {self.params['name']}")
                    elif request == "пока":
                        self.write_msg(user=user_id, text=f"Пока, {self.api.get_user_info(user_id)}")
                    elif request == "поиск":
                        users = self.api.search_users(self.params)
                        self.write_msg(user_id,
                                       f'Найдено {len(users)} пользователей. Введите "следующий" для просмотра следующего пользователя')
                    elif request == 'следующий' and users:
                        user = users.pop(0)
                        db_handler = Handling(user_id, user['id'], user['photo_url'])
                        if db_handler.is_person_in_db():
                            continue
                        else:
                            db_handler.save_search_results()
                            photos_user = self.api.get_top_photos(user['id'])
                            self.write_msg(user_id, f'{user["name"]}\nСсылка на профиль: https://vk.com/id{user["id"]}',
                                           photos_user)
                    else:
                        self.write_msg(user_id, "Неизвестный запрос")


if __name__ == '__main__':
    front_api = VkFront(gr_token, vk_token)
    front_api.vk_long_poll()
