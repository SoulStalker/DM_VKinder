from random import randrange

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from auth import gr_token, vk_token
from backend import VkBackend


class VkFront:
    def __init__(self, gr_token, vk_token):
        self.interface = vk_api.VkApi(token=gr_token)
        self.api = VkBackend(vk_token)
        self.longpoll = VkLongPoll(self.interface)
        self.gr = self.interface.get_api()
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
        self.gr.messages.send(
            user_id=user,
            message=text,
            # keybard=self.kb(),
            attachment=url,
            random_id=randrange(10 ** 7)
        )

    def vk_long_poll(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    request = event.text.lower()
                    user_id = event.user_id
                    if request == "привет" or request == "start":
                        # keyboard = VkKeyboard()
                        # keyboard.add_button("Поиск", color=VkKeyboardColor.NEGATIVE)
                        # keyboard.add_line()
                        self.params = self.api.get_user_info(user_id)
                        self.write_msg(user=user_id, text=f"Привет, {self.params['name']}")
                    elif request == "пока":
                        self.write_msg(user=user_id, text=f"Пока, {self.api.get_user_info(user_id)}")
                    elif request == "поиск":
                        # users = self.api.search_users(self.params)
                        # user = users.pop()
                        # photos_user = self.api.get_top_photos(user['id'])
                        # self.write_msg(user_id, photos_user)
                        self.write_msg(user_id, 'работаю...')
                    else:
                        VkFront.write_msg(user_id, "Неизвестный запрос...")


if __name__ == '__main__':
    front_api = VkFront(gr_token, vk_token)
    front_api.vk_long_poll()
