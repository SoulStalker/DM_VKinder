from random import randrange

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType


class VkApiClient:
    def __init__(self, token: str, user_id: str):
        self.user_id = user_id
        self.token = token

    def get_user_info(self, user_id):
        pass

    def search_users(self, age, sex, city, status):
        pass

    def get_top_photos(self, user_id):
        pass


with open('vktoken.txt', encoding='utf-8') as vk_file:
    # токен ВК из файла
    vk_token = vk_file.read()

vk = vk_api.VkApi(token=vk_token)
longpoll = VkLongPoll(vk)


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7),})


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            request = event.text

            if request == "привет":
                write_msg(event.user_id, f"Хай, {event.user_id}")
            elif request == "пока":
                write_msg(event.user_id, "Пока((")
            else:
                write_msg(event.user_id, "Не поняла вашего ответа...")